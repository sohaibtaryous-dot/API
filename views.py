# -*- coding: utf-8 -*-
"""Page IMPORT : téléversement multi-formats, contrôle des fichiers, tableau TOUS_CLIENTS (25 colonnes), alertes,
groupes de documents, synthèse par fournisseur et export Excel / CSV."""

from __future__ import annotations

import hashlib
import traceback
from datetime import datetime

import pandas as pd
import streamlit as st

import app as core
import fileio
import shipment
import ui

NGP_COLS = ("NGP (REF_PAR_FRS)", "Onglet REF_PAR_FRS", "Contrôle NGP")
SEV_CSS = {0: "background-color: rgba(220,38,38,.22)", 1: "background-color: rgba(245,158,11,.16)"}


def _size(n: int) -> str:
    return f"{n / 1e6:.1f} Mo" if n >= 1e6 else f"{max(n / 1e3, 0.1):.0f} Ko"


def files_overview(files) -> list[str]:
    """Affiche le contrôle de chaque fichier avant traitement ; renvoie les noms des fichiers inutilisables."""
    rows, bad = [], []
    for f in files:
        try:
            data = f.getvalue()
            kind = fileio.validate_upload(f.name, data)
            rows.append({"name": f.name, "type": fileio.KIND_LABEL.get(kind, kind), "size": _size(len(data)),
                         "ok": True, "message": ""})
        except fileio.FileReadError as exc:
            bad.append(f.name)
            rows.append({"name": f.name, "type": "?", "size": "", "ok": False, "message": str(exc)})
        except Exception as exc:  # fichier impossible à lire côté navigateur
            bad.append(f.name)
            rows.append({"name": f.name, "type": "?", "size": "", "ok": False, "message": f"lecture impossible ({type(exc).__name__})"})
    ui.file_list(rows)
    return bad


def clean_edited(edited: pd.DataFrame) -> pd.DataFrame:
    """Tableau modifié par l'utilisateur -> types propres (nombres, entiers, textes)."""
    edited = edited.copy()
    for c in core.EDITABLE_COLUMNS:
        if c not in edited.columns:
            edited[c] = None
    for c in core.NUMERIC_COLUMNS:
        if c in edited.columns:
            edited[c] = pd.to_numeric(edited[c], errors="coerce")
    for c in core.INT_COLUMNS:
        if c in edited.columns:
            edited[c] = pd.to_numeric(edited[c], errors="coerce").fillna(0).astype(int)
    for c in core.EDITABLE_COLUMNS:
        if c not in core.NUMERIC_COLUMNS and c not in core.INT_COLUMNS and c in edited.columns:
            edited[c] = edited[c].map(core.clean_cell)
    cols = [c for c in core.EDITABLE_COLUMNS if c in edited.columns] + [c for c in core.INTERNAL_COLUMNS if c in edited.columns]
    return edited[cols]


def _column_config(n_pages: int) -> dict:
    cfg = {"Qté": st.column_config.NumberColumn("Qté", format="%.3f"),
           "Prix unitaire": st.column_config.NumberColumn("Prix unitaire", format="%.4f"),
           "Valeur HT": st.column_config.NumberColumn("Valeur HT", format="%.2f"),
           core.C_NETU: st.column_config.NumberColumn(core.C_NETU, format="%.4f"),
           core.C_COLIS: st.column_config.NumberColumn(core.C_COLIS, format="%d"),
           "Page PDF": st.column_config.NumberColumn("Page PDF", format="%d"),
           core.PAGE_IN_PDF: st.column_config.NumberColumn(
               f"{core.PAGE_IN_PDF} ({n_pages} p.)" if n_pages else core.PAGE_IN_PDF, format="%d"),
           core.C_BASE: st.column_config.TextColumn(core.C_BASE, width="large")}
    for c in (core.C_NET, core.C_NETF, core.C_GROSSF, core.C_MANIF):
        cfg[c] = st.column_config.NumberColumn(c, format="%.3f")
    return cfg


def _style_view(view: pd.DataFrame, sev: pd.Series):
    """Surlignage ligne à ligne : rouge = critique, orange = à vérifier ; NGP comme avant."""
    fmt2 = lambda v: "" if pd.isna(v) else f"{v:,.2f}".replace(",", " ")  # noqa: E731
    fmt3 = lambda v: "" if pd.isna(v) else f"{v:,.3f}".replace(",", " ")  # noqa: E731
    fmt = {c: fmt2 for c in ("Prix unitaire", "Valeur HT")}
    fmt.update({c: fmt3 for c in (core.C_NET, core.C_NETU, core.C_NETF, core.C_GROSSF, core.C_MANIF, "Qté")})

    def row_style(row):
        styles = core.highlight_rows(row)
        css = SEV_CSS.get(int(sev.get(row.name, 9)))
        if css:
            cols = list(row.index)
            for k, c in enumerate(cols):
                if c in ("Item", "Réf article", "Remarque", core.C_BASE, core.C_NET, core.C_NETF, core.C_GROSSF):
                    styles[k] = f"{styles[k]};{css};font-weight:600" if styles[k] else f"{css};font-weight:600"
        return styles
    return view.style.apply(row_style, axis=1).format(fmt, na_rep="")


def render_import(ocr, ai_cfg, ai_label: str, basis: str):
    result0 = st.session_state.get("result")

    # ---------------- En-tête
    if result0:
        s0 = core.compute_summary(core.apply_matching(result0["lines"], result0["refdb"]))
        stats = {"lignes ventilées": s0["lignes"], "factures": s0["factures"], "fournisseurs": s0["fournisseurs"],
                 "alertes": sum(1 for a in result0.get("alerts", []) if a["Sévérité"] != "Info")}
    else:
        stats = {"formats": "PDF · Excel · Word", "langues": "toutes", "lecture": "IA + contrôles" if ai_cfg else "règles",
                 "feuille Excel": "25 colonnes"}
    ui.hero_3d(stats, ai_label=ai_label)

    # ---------------- Imports
    c1, c2 = st.columns(2, gap="medium")
    with c1:
        with st.container(key="card_upl_pdf"):
            ui.card_title("📂", "Dossier complet de la remorque",
                          "Factures, Packing Lists, BL, Manifeste — un ou plusieurs fichiers, tous formats",
                          ["PDF", "PDF scanné", "Excel", "Word", "CSV", "Images"])
            files = st.file_uploader("Dossier complet (PDF, Excel, Word, CSV, images)", type=fileio.UPLOAD_TYPES,
                                     accept_multiple_files=True, key="imp_files")
    with c2:
        with st.container(key="card_upl_ref"):
            ui.card_title("📗", "Référentiel articles & NGP",
                          "Importer le fichier Excel de référence (Références & NGP)",
                          ["Réf Article", "Réf Alstom (PN)", "Code NGP", ".xlsx / .xls / .csv"])
            ref_file = st.file_uploader("Référentiel Excel (Références & NGP)", type=["xlsx", "xlsm", "xls", "csv"],
                                        key="imp_ref")
    bad = files_overview(files) if files else []
    usable = [f for f in (files or []) if f.name not in bad]
    if files and bad:
        st.warning(f"{len(bad)} fichier(s) inutilisable(s) seront ignorés : corrigez-les ou retirez-les de la liste.")

    done = "result" in st.session_state
    ui.steps_strip(2 if done else (1 if usable else 0))
    launch = st.button("Lancer la ventilation du dossier", type="primary", use_container_width=True,
                       disabled=not usable, icon=":material/play_arrow:")
    if usable and not ref_file:
        st.caption("Sans fichier de référence, toutes les lignes seront « NON TROUVÉ ».")

    if launch:
        progress = st.progress(0.0, text="Initialisation...")
        try:
            result = core.run_pipeline(usable, ref_file, ocr, basis, progress, ai_cfg)
        except Exception as exc:  # garde-fou : l'application ne doit jamais « planter »
            progress.empty()
            st.error(f"Le traitement n'a pas pu aboutir ({type(exc).__name__}: {exc}). Vos fichiers n'ont pas été "
                     "modifiés. Retirez le fichier en cause (voir la liste ci-dessus) ou convertissez-le en PDF / Excel, "
                     "puis relancez.")
            with st.expander("Détail technique (à transmettre au support)"):
                st.code(traceback.format_exc())
            return
        final0 = core.apply_matching(result["lines"], result["refdb"])
        st.session_state["result"] = result
        st.session_state["lines_edit"] = final0
        st.session_state["manifest_edit"] = result["manifest"]
        st.session_state["editor_version"] = st.session_state.get("editor_version", 0) + 1
        st.session_state.pop("xlsx_sig", None)
        progress.progress(1.0, text="✅ Traitement terminé.")
        st.rerun()

    if "result" not in st.session_state:
        return
    result = st.session_state["result"]
    ver = st.session_state.get("editor_version", 0)
    n_pages = result.get("n_pages", 0)
    issues = result.get("issues") or []

    top = st.container()
    tabs = st.tabs([":material/dashboard: Résumé", ":material/table_rows: Tableau TOUS_CLIENTS",
                    ":material/visibility: Contrôle visuel", ":material/notification_important: Alertes",
                    ":material/hub: Groupes de documents", ":material/receipt_long: Manifeste",
                    ":material/fact_check: Analyse IA", ":material/folder_open: Fichiers & journal"])
    t_sum, t_edit, t_view, t_alert, t_grp, t_man, t_ai, t_files = tabs

    # ---------------- Tableau modifiable + manifeste
    with t_edit:
        st.caption("Corrigez ou complétez : NGP, contrôles, alertes et classeur Excel sont recalculés automatiquement. "
                   "Colonnes jaunes (NGP référentiel) calculées. Lignes ajoutables / supprimables.")
        edited = st.data_editor(
            st.session_state["lines_edit"], num_rows="dynamic", use_container_width=True, height=540,
            key=f"lines_editor_{ver}", column_order=core.COLUMNS, disabled=list(NGP_COLS),
            column_config=_column_config(n_pages))
    with t_man:
        st.caption("Poids brut et Goods Value du manifeste par fournisseur (extraits si le manifeste contient un "
                   "tableau, sinon à saisir). Rattachement automatique par nom proche.")
        man_edit = st.data_editor(
            st.session_state["manifest_edit"], num_rows="dynamic", use_container_width=True, key=f"manifest_editor_{ver}",
            column_config={"Goods Value": st.column_config.NumberColumn(format="%.2f"),
                           "Poids (kg)": st.column_config.NumberColumn(format="%.3f")})

    final = core.apply_matching(clean_edited(edited), result["refdb"])
    man_final = man_edit.copy()
    for c in ("Goods Value", "Poids (kg)", "Colis"):
        if c in man_final.columns:
            man_final[c] = pd.to_numeric(man_final[c], errors="coerce")
    for c in ("Expéditeur", "Shipment", "Devise"):
        if c in man_final.columns:
            man_final[c] = man_final[c].map(core.clean_cell)
    alerts_df = shipment.collect_alerts(result.get("alerts", []), shipment.live_alerts(final), issues)
    sev_map = shipment.severity_map(alerts_df)
    sev = final.apply(lambda r: shipment.row_severity(r, sev_map), axis=1) if len(final) else pd.Series(dtype=int)

    # ---------------- Classeur Excel (reconstruit seulement si le contenu change)
    sig = hashlib.md5((final.astype(str).to_csv() + man_final.astype(str).to_csv() + alerts_df.astype(str).to_csv()).encode()).hexdigest()
    if st.session_state.get("xlsx_sig") != sig:
        try:
            st.session_state["xlsx"] = core.build_workbook(final, man_final, result.get("docs"), n_pages, alerts_df,
                                                           result.get("groups"))
            st.session_state["xlsx_sig"] = sig
        except Exception as exc:
            st.session_state["xlsx"] = None
            st.session_state["xlsx_sig"] = None
            st.error(f"Génération du classeur Excel impossible ({type(exc).__name__}: {exc}).")
    xlsx = st.session_state.get("xlsx")
    s = core.compute_summary(final)
    n_crit = int((alerts_df["Sévérité"] == "Critique").sum()) if not alerts_df.empty else 0
    n_warn = int((alerts_df["Sévérité"] == "Avertissement").sum()) if not alerts_df.empty else 0
    n_info = int((alerts_df["Sévérité"] == "Info").sum()) if not alerts_df.empty else 0

    # ---------------- Bandeau de statut + téléchargements (1 clic)
    with top:
        n_err = sum(1 for i in issues if i.get("Gravité") == "Erreur")
        if n_err:
            ui.status_banner("ko", "", f"{n_err} fichier(s) ignoré(s) ou illisible(s)",
                             "Voir l'onglet « Fichiers & journal » pour la cause et la marche à suivre.")
        if not s["lignes"]:
            ui.status_banner("ko", "", "Aucune ligne de facture extraite",
                             "Consultez « Fichiers & journal » ou ajoutez les lignes à la main dans le tableau.")
        elif n_crit:
            ui.status_banner("ko", "", f"{n_crit} alerte(s) critique(s) à traiter avant déclaration",
                             f"{n_warn} avertissement(s) · voir l'onglet « Alertes ». Les lignes concernées sont surlignées.")
        elif n_warn or s["non_trouves"] or s["ecarts"]:
            ui.status_banner("warn", "", "Dossier à vérifier",
                             f"{n_warn} avertissement(s) · {s['non_trouves']} NON TROUVÉ · {s['ecarts']} écart(s) NGP.")
        else:
            ui.status_banner("ok", "", "Dossier conforme", "Aucune alerte : prêt pour la déclaration.")
        stamp = datetime.now().strftime("%Y%m%d_%H%M")
        d1, d2 = st.columns([2.2, 1])
        with d1:
            st.download_button("Télécharger TOUS_CLIENTS (.xlsx)", data=xlsx or b"", disabled=not xlsx,
                               file_name=f"TOUS_CLIENTS_{stamp}.xlsx", icon=":material/download:",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                               type="primary", use_container_width=True, key="dl_xlsx")
        with d2:
            csv_bytes = final[core.COLUMNS].to_csv(sep=";", index=False, decimal=",").encode("utf-8-sig")
            st.download_button("CSV (Excel FR)", data=csv_bytes, file_name=f"TOUS_CLIENTS_{stamp}.csv",
                               mime="text/csv", use_container_width=True, icon=":material/csv:", key="dl_csv")

    # ---------------- Résumé
    with t_sum:
        pct_ok = round(100 * s["ok"] / s["lignes"]) if s["lignes"] else 0
        ui.kpi_cards([
            {"icon": "list", "label": "Lignes extraites", "value": s["lignes"], "sub": "individualisées", "tone": "blue"},
            {"icon": "file", "label": "Factures", "value": s["factures"], "sub": f"{result.get('n_files', 0)} fichier(s) · {n_pages} p.", "tone": "cyan"},
            {"icon": "building", "label": "Fournisseurs", "value": s["fournisseurs"], "sub": "expéditeurs", "tone": "gold"},
            {"icon": "alert", "label": "Alertes critiques", "value": n_crit, "sub": f"{n_warn} avertissement(s)",
             "tone": "bad" if n_crit else ("warn" if n_warn else "good")},
            {"icon": "help", "label": "NON TROUVÉ", "value": s["non_trouves"],
             "sub": "à créer dans le référentiel" if s["non_trouves"] else "aucun", "tone": "warn" if s["non_trouves"] else "good"},
            {"icon": "check", "label": "Contrôle NGP OK", "value": f"{pct_ok} %", "sub": f"{s['ok']} / {s['lignes']} lignes",
             "tone": "good" if pct_ok == 100 else "blue"},
        ])
        cards2 = [{"icon": "banknote", "label": f"Valeur HT {dev or '(devise ?)'}", "value": round(float(tot), 2), "decimals": 2,
                   "sub": "total des lignes", "tone": "blue"} for dev, tot in s["par_devise"].items()][:3]
        cards2 += [{"icon": "scale", "label": "Poids net total", "value": round(s["poids_net"], 3), "decimals": 3,
                    "sub": "kg · Σ lignes", "tone": "cyan"},
                   {"icon": "package", "label": "Poids brut factures", "value": round(s["poids_brut"], 3), "decimals": 3,
                    "sub": "kg · Σ factures", "tone": "gold"}]
        if cards2:
            ui.kpi_cards(cards2[:6])
        ui.section("Synthèse par fournisseur / client", "building")
        ui.supplier_cards(shipment.supplier_summary(final, alerts_df))
        if len(final):
            final_for_ui = final.rename(columns={"Client": "Fournisseur / Expéditeur", "N° facture": "N° Facture",
                                                 "NGP (REF_PAR_FRS)": "NGP (Excel Réf)"}).assign(
                Devise=final["_devise"] if "_devise" in final.columns else "")
            g1, g2 = st.columns([1.5, 1], gap="medium")
            with g1:
                with st.container(key="card_chart_val"):
                    ui.card_title("💶", "Valeur HT par fournisseur", "Survolez une barre pour le détail")
                    try:
                        ui.chart_value_by_supplier(final_for_ui)
                    except Exception:
                        st.write(final_for_ui.groupby("Fournisseur / Expéditeur")["Valeur HT"].sum().to_frame())
            with g2:
                with st.container(key="card_chart_ngp"):
                    ui.card_title("🎯", "Contrôle NGP", "Répartition des lignes par statut")
                    try:
                        ui.chart_ngp_status(final_for_ui)
                    except Exception:
                        st.write(final_for_ui["Contrôle NGP"].value_counts().to_frame())

    # ---------------- Contrôle visuel (lecture seule, filtres, surlignage)
    with t_view:
        f1, f2, f3 = st.columns([2, 1.2, 1.4])
        sups = sorted({core.clean_cell(c) or "À compléter" for c in final["Client"]}) if len(final) else []
        pick = f1.multiselect("Fournisseur / client", sups, default=[], placeholder="Tous", key=f"f_sup_{ver}")
        only = f2.toggle("Lignes en alerte seulement", value=False, key=f"f_alert_{ver}")
        query = f3.text_input("Recherche (réf, désignation, n° facture)", key=f"f_q_{ver}")
        view = final[core.COLUMNS].copy()
        mask = pd.Series(True, index=view.index)
        if pick:
            mask &= final["Client"].map(lambda c: core.clean_cell(c) or "À compléter").isin(pick)
        if only and len(sev):
            mask &= sev.lt(9)
        if query.strip():
            q = query.strip().lower()
            mask &= view[["Réf article", "Désignation", "N° facture"]].astype(str).apply(
                lambda col: col.str.lower().str.contains(q, regex=False)).any(axis=1)
        view = view[mask]
        st.caption(f"{len(view)} ligne(s) affichée(s) sur {len(final)} — rouge : alerte critique · orange : à vérifier. "
                   "Survolez le N° de facture / la colonne « Base / remarque poids » pour l'origine de chaque poids.")
        if len(view):
            st.dataframe(_style_view(view, sev), use_container_width=True, height=560, hide_index=True)
        else:
            st.info("Aucune ligne ne correspond aux filtres.")

    # ---------------- Alertes
    with t_alert:
        ui.kpi_cards([
            {"icon": "alert", "label": "Critiques", "value": n_crit, "sub": "à traiter avant déclaration", "tone": "bad" if n_crit else "good"},
            {"icon": "alert", "label": "Avertissements", "value": n_warn, "sub": "à vérifier", "tone": "warn" if n_warn else "good"},
            {"icon": "help", "label": "Infos", "value": n_info, "sub": "pour information", "tone": "blue"},
        ])
        if alerts_df.empty:
            ui.status_banner("ok", "", "Aucune alerte", "Poids, calculs, liaison des documents et fichiers : tout est cohérent.")
        else:
            sev_pick = st.multiselect("Sévérité", list(shipment.SEV_ORDER), default=["Critique", "Avertissement"],
                                      key=f"a_sev_{ver}")
            types = sorted(alerts_df["Type"].unique())
            typ_pick = st.multiselect("Type", types, default=[], placeholder="Tous", key=f"a_typ_{ver}")
            av = alerts_df[alerts_df["Sévérité"].isin(sev_pick)]
            if typ_pick:
                av = av[av["Type"].isin(typ_pick)]
            av = av.copy()
            av.insert(0, " ", av["Sévérité"].map(shipment.SEV_ICON))
            st.dataframe(av, use_container_width=True, hide_index=True, height=480,
                         column_config={" ": st.column_config.TextColumn(" ", width="small"),
                                        "Message": st.column_config.TextColumn("Message", width="large")})
            st.caption("Écarts de poids : facture ↔ packing list / BL ↔ manifeste (tolérance 50 g ou 0,5 %). "
                       "Corrigez le tableau : les alertes se recalculent.")

    # ---------------- Groupes de documents
    with t_grp:
        groups = result.get("groups")
        if groups is None or groups.empty:
            st.info("Aucun groupe de documents (aucune facture détectée).")
        else:
            n_ok = int(groups["Statut"].astype(str).str.startswith("✅").sum())
            ui.kpi_cards([
                {"icon": "layers", "label": "Groupes (factures)", "value": len(groups), "sub": "facture + documents liés", "tone": "blue"},
                {"icon": "check", "label": "Complets", "value": n_ok, "sub": "facture + packing list/BL cohérents", "tone": "good"},
                {"icon": "alert", "label": "À vérifier", "value": len(groups) - n_ok, "sub": "documents manquants ou écart", "tone": "warn" if len(groups) - n_ok else "good"},
            ])
            st.caption("Chaque facture est reliée automatiquement à son BL / packing list (n° cité, fournisseur, proximité) "
                       "et au manifeste (nom du fournisseur). Le poids manquant sur une ligne est repris de la packing list / du BL.")
            gcfg = {c: st.column_config.NumberColumn(c, format="%.3f") for c in groups.columns if c.startswith("Poids")}
            gcfg["Packing list / BL liés"] = st.column_config.TextColumn("Packing list / BL liés", width="large")
            st.dataframe(groups, use_container_width=True, hide_index=True, height=360, column_config=gcfg)
            ui.section("Par fournisseur", "building")
            for sup, g in groups.groupby("Fournisseur", sort=False):
                ok = g["Statut"].astype(str).str.startswith("✅").all()
                with st.expander(f"{'✅' if ok else '⚠️'}  {core.clean_cell(sup) or 'À compléter'} — {len(g)} facture(s)"):
                    for _, r in g.iterrows():
                        st.markdown(f"**Facture {r['N° facture'] or '—'}** · {r['Facture']}  \n"
                                    f"Packing list / BL : {r['Packing list / BL liés']}  \n"
                                    f"Manifeste : {r['Manifeste']}  \n{r['Statut']}")

    with t_ai:
        core.render_audit(result.get("audit") or [])

    with t_files:
        if issues:
            ui.section("Problèmes de fichiers", "alert")
            st.dataframe(pd.DataFrame(issues), use_container_width=True, hide_index=True,
                         column_config={"Problème": st.column_config.TextColumn(width="large"),
                                        "Que faire": st.column_config.TextColumn(width="large")})
        else:
            st.success("Tous les fichiers ont été lus sans problème.")
        ui.section("Documents détectés dans le dossier", "layers")
        st.dataframe(result["docs"], use_container_width=True, hide_index=True)
        st.caption(f"Référentiel chargé : {result['refdb']['count']} références.")
        ui.section("Journal de traitement", "list")
        for msg in result["log"]:
            st.write(msg)
