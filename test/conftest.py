import pytest
# Remplacez 'app' par le nom de votre fichier principal si différent
from app import app as flask_app


@pytest.fixture
def client():
    # On configure l'app pour le mode test
    flask_app.config.update({
        "TESTING": True,
    })

    # Le test_client de Flask simule les requêtes HTTP sans lancer de serveur réel
    with flask_app.test_client() as client:
        yield client
