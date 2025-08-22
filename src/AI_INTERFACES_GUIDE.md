# Guide d'Utilisation des Interfaces IA

## 🚀 Vue d'ensemble

Les interfaces IA permettent d'utiliser les services d'intelligence artificielle intégrés dans l'application de gestion des congés et tickets TUNISAIR Express.

## 📋 Interfaces Disponibles

### 1. Analytics IA (`/dashboard/ai/analytics/`)
- **Accès**: Superuser uniquement
- **Fonction**: Dashboard complet avec KPI et graphiques des analyses IA
- **Fonctionnalités**:
  - Statistiques des congés et tickets analysés
  - Distribution des priorités et sentiments
  - Insights automatiques
  - Export des données

### 2. Test IA (`/dashboard/ai/test-interface/`)
- **Accès**: Superuser uniquement
- **Fonction**: Interface de test pour tous les services IA
- **Fonctionnalités**:
  - Analyse de sentiment en temps réel
  - Prédiction de priorité
  - Catégorisation automatique
  - Prédiction d'approbation de congé
  - Analyse par lot

### 3. Traitement par Lot IA (`/dashboard/ai/batch-processing/`)
- **Accès**: Superuser uniquement
- **Fonction**: Traitement automatique des données existantes
- **Fonctionnalités**:
  - Analyse de tous les congés
  - Analyse de tous les tickets
  - Génération d'insights
  - Détection d'anomalies

### 4. Analyse Temps Réel IA (`/dashboard/ai/realtime-analysis/`)
- **Accès**: Superuser uniquement
- **Fonction**: Interface d'analyse en temps réel
- **Fonctionnalités**:
  - Saisie de texte en temps réel
  - Analyse automatique après 2 secondes d'inactivité
  - Historique des analyses
  - Statistiques en temps réel

## 🔧 Utilisation des Interfaces

### Interface de Test IA

1. **Accéder à l'interface**:
   ```
   http://localhost:8000/dashboard/ai/test-interface/
   ```

2. **Analyse de sentiment**:
   - Sélectionner "Analyse de Sentiment"
   - Entrer le texte à analyser
   - Cliquer sur "Analyser"
   - Consulter les résultats (sentiment, score, confiance)

3. **Prédiction de priorité**:
   - Sélectionner "Prédiction de Priorité"
   - Entrer le texte
   - Optionnel: spécifier le rôle utilisateur et type de ticket
   - Consulter les résultats (priorité, score, raison)

4. **Catégorisation automatique**:
   - Sélectionner "Catégorisation Automatique"
   - Entrer le texte
   - Optionnel: spécifier la destination
   - Consulter les résultats (catégorie, confiance)

5. **Prédiction d'approbation de congé**:
   - Remplir les informations employé et congé
   - Cliquer sur "Prédire"
   - Consulter la probabilité d'approbation et les facteurs

### Interface de Traitement par Lot

1. **Accéder à l'interface**:
   ```
   http://localhost:8000/dashboard/ai/batch-processing/
   ```

2. **Analyser tous les congés**:
   - Cliquer sur "Analyser les Congés"
   - Confirmer l'action
   - Attendre le traitement
   - Consulter les statistiques mises à jour

3. **Analyser tous les tickets**:
   - Cliquer sur "Analyser les Tickets"
   - Confirmer l'action
   - Attendre le traitement
   - Consulter les statistiques mises à jour

4. **Générer des insights**:
   - Cliquer sur "Générer Insights"
   - Consulter les insights automatiques

5. **Détecter les anomalies**:
   - Cliquer sur "Détecter Anomalies"
   - Consulter les anomalies détectées

### Interface d'Analyse Temps Réel

1. **Accéder à l'interface**:
   ```
   http://localhost:8000/dashboard/ai/realtime-analysis/
   ```

2. **Saisir du texte**:
   - Entrer le texte dans la zone de saisie
   - L'analyse se lance automatiquement après 2 secondes

3. **Choisir le type d'analyse**:
   - Sentiment: analyse du sentiment du texte
   - Priorité: prédiction de la priorité
   - Catégorie: catégorisation automatique

4. **Consulter les résultats**:
   - Les résultats s'affichent en temps réel
   - L'historique est conservé
   - Les statistiques sont mises à jour

## 📊 Services IA Disponibles

### 1. Analyse de Sentiment
- **Fonction**: Analyse le sentiment d'un texte
- **Retour**: `{'sentiment': 'positive/negative/neutral', 'score': float, 'confidence': float}`
- **Utilisation**: Textes de tickets, descriptions de congés

### 2. Prédiction de Priorité
- **Fonction**: Prédit la priorité d'un ticket
- **Retour**: `{'priority': 'low/medium/high/urgent', 'score': float, 'reason': str}`
- **Utilisation**: Tickets, demandes urgentes

### 3. Catégorisation Automatique
- **Fonction**: Catégorise automatiquement un ticket
- **Retour**: `{'category': str, 'confidence': float}`
- **Utilisation**: Classification des tickets

### 4. Prédiction d'Approbation de Congé
- **Fonction**: Prédit la probabilité d'approbation d'un congé
- **Retour**: `{'approval_probability': float, 'factors': list}`
- **Utilisation**: Demandes de congés

## 🔍 Champs IA dans les Modèles

### Modèle Leave (Congés)
```python
ai_approval_probability = models.FloatField(default=0.0)
ai_approval_factors = models.TextField(blank=True, null=True)
ai_priority = models.CharField(max_length=20, blank=True, null=True)
ai_priority_score = models.FloatField(default=0.0)
ai_analysis_date = models.DateTimeField(null=True, blank=True)
```

### Modèle Ticket
```python
ai_priority = models.CharField(max_length=20, blank=True, null=True)
ai_priority_score = models.FloatField(default=0.0)
ai_priority_reason = models.TextField(blank=True, null=True)
ai_category = models.CharField(max_length=50, blank=True, null=True)
ai_category_confidence = models.FloatField(default=0.0)
ai_sentiment = models.CharField(max_length=20, blank=True, null=True)
ai_sentiment_score = models.FloatField(default=0.0)
ai_analysis_date = models.DateTimeField(null=True, blank=True)
```

## 🛠️ Configuration

### Paramètres IA (dans `ai_config.py`)
```python
SENTIMENT_THRESHOLD = 0.1
PRIORITY_THRESHOLD = 0.5
CONFIDENCE_THRESHOLD = 0.7
ANOMALY_THRESHOLD = 2.0
```

### Mots-clés de Priorité
```python
PRIORITY_KEYWORDS = {
    'urgent': ['urgent', 'critique', 'panne', 'bloqué'],
    'high': ['important', 'priorité', 'problème'],
    'medium': ['demande', 'information'],
    'low': ['question', 'curiosité']
}
```

## 🧪 Tests

### Exécuter les tests automatiques
```bash
python manage.py test dashboard.test_ai_interfaces
```

### Exécuter les tests manuels
```bash
python manage.py shell
>>> from dashboard.test_ai_interfaces import run_manual_tests
>>> run_manual_tests()
```

## 📈 Monitoring

### Statistiques disponibles
- Nombre de congés analysés
- Nombre de tickets analysés
- Taux d'analyse global
- Distribution des priorités
- Distribution des sentiments
- Insights générés

### Logs
Les actions IA sont loggées dans les logs Django. Consulter les logs pour:
- Erreurs d'analyse
- Performance des services
- Utilisation des interfaces

## 🔒 Sécurité

### Accès
- Toutes les interfaces IA sont réservées aux superusers
- Vérification d'authentification sur chaque vue
- Protection CSRF sur tous les formulaires

### Données
- Les données d'analyse sont stockées en base
- Pas de données personnelles sensibles dans les analyses
- Chiffrement des configurations sensibles

## 🚨 Dépannage

### Problèmes courants

1. **Service IA non disponible**
   - Vérifier l'installation des dépendances
   - Consulter les logs d'erreur
   - Redémarrer le serveur

2. **Erreurs d'analyse**
   - Vérifier la validité du texte d'entrée
   - Consulter les paramètres de configuration
   - Tester avec des exemples simples

3. **Performance lente**
   - Vérifier la charge du serveur
   - Optimiser les requêtes de base de données
   - Considérer l'utilisation de cache

### Support
Pour toute question ou problème:
- Consulter la documentation technique
- Vérifier les logs d'erreur
- Contacter l'équipe de développement

## 📝 Notes de Version

### Version 1.0
- ✅ Interfaces de test IA
- ✅ Traitement par lot
- ✅ Analyse temps réel
- ✅ Dashboard analytics
- ✅ Intégration complète des services

### Prochaines fonctionnalités
- 🔄 Interface d'administration des paramètres IA
- 🔄 Export des résultats d'analyse
- 🔄 Notifications automatiques
- 🔄 API REST pour intégration externe 