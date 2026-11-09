# Suivi de budget

Application desktop en Python (PySide6/Qt + SQLite) de suivi de budget multi-comptes :
compte commun et compte perso, import d'exports bancaires Crédit Agricole, catégorisation
automatique, virements perso → commun, vues mensuelle et annuelle, exports Excel.

## Installation

```bash
pip install -r requirements.txt
```

## Lancement

```bash
python main.py
```

La base SQLite (`budget.db`) est créée automatiquement à la racine du projet au premier lancement.

## Fonctionnalités

- **Multi-comptes** : compte commun + compte(s) perso, extensibles (onglet « Comptes & cartes »).
- **Import bancaire** (onglet « Import bancaire ») : fichiers `.xls` (xlrd), `.xlsx` (openpyxl)
  et `.csv` (détection automatique du séparateur `;` ou `,`), format Crédit Agricole :
  ligne de titre ignorée, libellés multi-lignes aplatis, montants avec espaces insécables
  gérés (`1 234,56 €`), cartes reconnues via le masque `X2121`.
- **Catégorisation automatique** par mots-clés, avec apprentissage.
- **Virements perso → commun** détectés automatiquement à l'import (« VIREMENT ... JEAN »).
- **Vues mensuelle et annuelle** avec totaux par catégorie et solde.
- **Exports Excel** (`.xlsx`) du mois ou de l'année.

## Tests

```bash
./run_tests.sh
```

## Structure

```
budget-app/
├── main.py               # point d'entrée (python main.py)
├── budget_app/
│   ├── db.py             # couche SQLite (comptes, catégories, opérations, virements)
│   ├── importer.py       # import .xls/.xlsx/.csv Crédit Agricole
│   ├── categorizer.py    # catégorisation auto + apprentissage
│   ├── transfers.py      # détection des virements perso <-> commun
│   ├── reports.py        # agrégats mensuels / annuels
│   ├── exporters.py      # exports Excel
│   └── ui/               # fenêtre Qt : 7 onglets
├── tests/                # tests unitaires (unittest)
├── samples/              # exemples d'exports bancaires
├── run_tests.sh
└── requirements.txt
```
