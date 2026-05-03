# 🤝 Guide de contribution — AirSentinel CM

Merci de contribuer à AirSentinel CM !

## Comment contribuer

### 1. Forker le dépôt
Cliquez sur **Fork** en haut à droite de la page GitHub.

### 2. Cloner votre fork
```bash
git clone https://github.com/LEUMENI/airsentinel-cm.git
cd airsentinel-cm
```

### 3. Créer une branche
```bash
git checkout -b feature/nom-de-votre-feature
```

### 4. Faire vos modifications
- Respectez la structure du projet
- Ajoutez des tests si nécessaire
- Documentez vos changements

### 5. Tester
```bash
pip install -r requirements.txt
python -m pytest tests/
streamlit run app.py
```

### 6. Pousser et créer une Pull Request
```bash
git add .
git commit -m "feat: description de votre modification"
git push origin feature/nom-de-votre-feature
```

Puis créez une **Pull Request** sur GitHub.

## Standards de code

- Python 3.11+
- PEP 8 pour le style
- Commentaires en français ou anglais
- Tests unitaires pour les nouvelles fonctions ML

## Structure des commits

```
feat: nouvelle fonctionnalité
fix: correction de bug
docs: documentation
test: ajout de tests
refactor: refactoring
```

## Contact

Équipe InsightX D_Vas - IndabaX Cameroon 2026
