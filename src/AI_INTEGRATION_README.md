# Intégration IA - Système de Gestion TUNISAIR Express

## Vue d'ensemble

L'intégration IA dans le système de gestion des congés et tickets de TUNISAIR Express fournit des capacités d'analyse automatique et de prédiction pour améliorer l'efficacité du traitement des demandes.

## Architecture IA

### 1. Services IA (`dashboard/ai_services.py`)

Le module principal des services IA contient :

- **Analyse de sentiment** : Analyse automatique du ton et de l'émotion dans les demandes
- **Prédiction de priorité** : Détermine automatiquement la priorité des tickets et congés
- **Catégorisation automatique** : Classe automatiquement les tickets par type
- **Prédiction d'approbation** : Prédit la probabilité d'approbation des congés
- **Détection d'anomalies** : Identifie les patterns inhabituels dans les données
- **Génération d'insights** : Produit des insights automatiques basés sur les données

### 2. Intégration IA (`dashboard/ai_integration.py`)

Module d'intégration qui connecte les services IA avec les vues et modèles :

- **Analyse automatique** : Déclenche automatiquement l'analyse lors de la création
- **Mise à jour des modèles** : Met à jour les champs IA dans les modèles
- **Formatage des données** : Prépare les données pour l'affichage
- **Gestion des erreurs** : Gère gracieusement les erreurs d'analyse

### 3. Reporting IA (`dashboard/reporting.py`)

Service de reporting avec intégration IA :

- **Rapports mensuels** : Inclut les statistiques IA
- **Rapports analytics** : Analyse des tendances avec insights IA
- **Export Excel/PDF** : Export des données avec analytics IA

## Fonctionnalités IA

### Analyse Automatique

#### Congés
- **Prédiction d'approbation** : Calcule la probabilité d'approbation basée sur :
  - Type d'employé (PS, CDI, etc.)
  - Durée du congé
  - Type de congé
  - Période de l'année
- **Priorité automatique** : Détermine la priorité basée sur le type et la durée
- **Facteurs d'approbation** : Liste les facteurs influençant la décision

#### Tickets
- **Analyse de sentiment** : Analyse le ton de la demande
- **Prédiction de priorité** : Détermine la priorité basée sur la destination et le contexte
- **Catégorisation automatique** : Classe le ticket (réservation, information, etc.)
- **Score de confiance** : Indique la fiabilité de l'analyse

### Interface Utilisateur

#### Messages d'Analyse
```python
# Exemple de message lors de la création d'un congé
messages.info(request, '✅ Analyse IA effectuée automatiquement - Priorité: {}, Probabilité d\'approbation: {}%'.format(
    instance.ai_priority or 'Non définie',
    int((instance.ai_approval_probability or 0) * 100)
))
```

#### Affichage des Données IA
Les templates affichent automatiquement :
- **Probabilité d'approbation** (pour les congés)
- **Priorité IA** avec code couleur
- **Sentiment** avec icônes
- **Catégorie** avec score de confiance
- **Facteurs d'analyse** détaillés

### Dashboard Analytics IA

#### Accès
- URL : `/dashboard/ai/analytics/`
- Réservé aux superusers
- Interface dédiée aux analytics IA

#### Fonctionnalités
- **KPI IA** : Nombre d'analyses, scores moyens
- **Insights automatiques** : Générés en temps réel
- **Graphiques** : Distribution des priorités et sentiments
- **Export** : Rapports Excel/PDF avec données IA

## API IA

### Endpoints Disponibles

#### 1. Analyse de Sentiment
```http
POST /dashboard/ai/analyze-sentiment/
Content-Type: application/json

{
    "text": "Texte à analyser"
}
```

**Réponse :**
```json
{
    "sentiment": "positive",
    "score": 0.8,
    "confidence": 0.9
}
```

#### 2. Prédiction de Priorité
```http
POST /dashboard/ai/predict-priority/
Content-Type: application/json

{
    "text": "Description du ticket",
    "user_role": "employee",
    "ticket_type": "reservation"
}
```

**Réponse :**
```json
{
    "priority": "high",
    "score": 0.75,
    "reason": "Destination internationale détectée"
}
```

#### 3. Catégorisation de Ticket
```http
POST /dashboard/ai/categorize-ticket/
Content-Type: application/json

{
    "text": "Description du ticket",
    "destination": "Paris"
}
```

**Réponse :**
```json
{
    "category": "reservation",
    "confidence": 0.85
}
```

#### 4. Prédiction d'Approbation de Congé
```http
POST /dashboard/ai/predict-leave-approval/
Content-Type: application/json

{
    "employee_data": {
        "employeetype": "PS"
    },
    "leave_data": {
        "leave_days": 5,
        "leavetype": "congé annuel",
        "startdate": "2024-07-01"
    }
}
```

**Réponse :**
```json
{
    "approval_probability": 0.85,
    "factors": ["Type d'employé: PS", "Congé court", "Période estivale"]
}
```

## Configuration IA

### Paramètres (`dashboard/ai_config.py`)

```python
# Seuil de sentiment
SENTIMENT_THRESHOLD = 0.1

# Mots-clés de priorité
PRIORITY_KEYWORDS = {
    'urgent': ['urgent', 'critique', 'immédiat'],
    'high': ['important', 'prioritaire', 'rapide'],
    'medium': ['normal', 'standard'],
    'low': ['non-urgent', 'flexible']
}

# Facteurs d'approbation
APPROVAL_FACTORS = {
    'employee_type': {
        'PS': 0.1,
        'CDI': 0.05,
        'CDD': 0.0
    },
    'duration': {
        'short': 0.1,
        'medium': 0.0,
        'long': -0.1
    }
}
```

## Modèles de Données IA

### Champs IA dans les Modèles

#### Leave Model
```python
# Champs IA
ai_approval_probability = models.FloatField(default=0.0)
ai_approval_factors = models.TextField(blank=True, null=True)
ai_priority = models.CharField(max_length=20, blank=True, null=True)
ai_priority_score = models.FloatField(default=0.0)
ai_analysis_date = models.DateTimeField(null=True, blank=True)
```

#### Ticket Model
```python
# Champs IA
ai_priority = models.CharField(max_length=20, blank=True, null=True)
ai_priority_score = models.FloatField(default=0.0)
ai_priority_reason = models.TextField(blank=True, null=True)
ai_category = models.CharField(max_length=50, blank=True, null=True)
ai_category_confidence = models.FloatField(default=0.0)
ai_sentiment = models.CharField(max_length=20, blank=True, null=True)
ai_sentiment_score = models.FloatField(default=0.0)
ai_analysis_date = models.DateTimeField(null=True, blank=True)
```

## JavaScript IA

### Script d'Analyse Temps Réel (`static_in_proj/our_static/js/ai_analytics.js`)

Fonctionnalités :
- **Analyse en temps réel** : Analyse automatique lors de la saisie
- **Indicateurs visuels** : Affichage des sentiments et priorités
- **Graphiques interactifs** : Visualisation des données IA
- **Gestion des erreurs** : Messages d'erreur gracieux

### Utilisation
```javascript
// Initialisation automatique
document.addEventListener('DOMContentLoaded', () => {
    new AIAnalytics();
});

// Analyse manuelle
function performAnalysis(type, id) {
    // Logique d'analyse
}
```

## Rapports IA

### Types de Rapports

#### 1. Rapport Mensuel
- Statistiques des congés et tickets
- Données IA intégrées
- Export Excel/PDF

#### 2. Rapport Analytics
- Tendances temporelles
- Insights IA automatiques
- Graphiques interactifs

### Templates de Rapports

#### Template Mensuel (`templates/dashboard/reports/monthly_report_template.html`)
- Section analytics IA
- Statistiques de probabilité d'approbation
- Distribution des priorités

#### Template Analytics (`templates/dashboard/reports/analytics_report_template.html`)
- Évolution temporelle
- Insights IA
- Comparaisons

## Sécurité et Performance

### Sécurité
- **Authentification requise** : Toutes les APIs IA nécessitent une authentification
- **Validation des données** : Validation stricte des entrées
- **Gestion des erreurs** : Messages d'erreur sécurisés

### Performance
- **Analyse asynchrone** : Les analyses lourdes sont effectuées en arrière-plan
- **Cache des résultats** : Mise en cache des analyses fréquentes
- **Optimisation des requêtes** : Requêtes optimisées pour les analytics

## Maintenance et Monitoring

### Logs
```python
# Exemple de logging IA
logger.info(f"Analyse IA terminée pour le congé {leave.id}")
logger.warning("Services AI désactivés")
logger.error(f"Erreur lors de l'analyse AI: {str(e)}")
```

### Monitoring
- **Taux de succès** : Suivi du taux de succès des analyses
- **Temps de réponse** : Monitoring des performances
- **Erreurs** : Alertes en cas d'erreur

## Évolutions Futures

### Améliorations Prévues
1. **Machine Learning avancé** : Modèles plus sophistiqués
2. **Analyse de documents** : Analyse des pièces jointes
3. **Prédiction de volume** : Anticipation des pics de demande
4. **Chatbot IA** : Assistant virtuel pour les utilisateurs

### Intégrations
1. **APIs externes** : Intégration avec des services IA tiers
2. **Bases de données** : Connexion avec des bases de données externes
3. **Systèmes tiers** : Intégration avec d'autres systèmes TUNISAIR

## Support et Documentation

### Contact
- **Équipe IA** : ia-team@tunisair.com
- **Documentation technique** : tech-docs.tunisair.com/ai
- **Support utilisateur** : support.tunisair.com

### Formation
- **Sessions de formation** : Mensuelles pour les nouveaux utilisateurs
- **Documentation utilisateur** : Guide complet disponible
- **Vidéos tutorielles** : Chaîne YouTube dédiée

---

*Documentation mise à jour le : {{ date }}*
*Version IA : 1.0.0* 