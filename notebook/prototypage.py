# faire les importations nécessaires
import psycopg2
import numpy as np

# Déclarer les variables nécessaires
conversation_file_path = "../data/DISTRIBUTION_ACCUEIL_UBS/TRANS_TXT/018_00000013.txt"
print(f"Chemin du fichier de conversation: {conversation_file_path}")

db_connection_str = "dbname=rag_chatbot user=postgres password=tasnim host=localhost port=5432"

def create_conversation_list(file_path: str) -> list[str]:
    """Lit un fichier texte en gérant l'encodage"""
    try:
        # Essayer en binaire et ignorer les erreurs
        with open(file_path, "rb") as file:
            raw_content = file.read()
            text = raw_content.decode('utf-8', errors='ignore')
            text_list = text.split("\n")
            filtered_list = [chaine.strip() for chaine in text_list if chaine.strip() and not chaine.startswith("<")]
            print(f"✅ Fichier lu avec {len(filtered_list)} conversations")
            return filtered_list
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return []

def calculate_embeddings(corpus: str) -> list[float]:
    """Simule des embeddings (pour le prototypage)"""
    # Crée un embedding aléatoire de 1536 dimensions (comme OpenAI)
    embedding = [float(np.random.normal(0, 0.1)) for _ in range(1536)]
    print(f"✅ Embedding simulé (1536 dimensions)")
    return embedding

def save_embedding(corpus: str, embedding: list[float], cursor) -> None:
    """Sauvegarde dans PostgreSQL"""
    try:
        embedding_array = "{" + ",".join(str(x) for x in embedding) + "}"
        cursor.execute(
            '''INSERT INTO embeddings (corpus, embedding) VALUES (%s, %s)''', 
            (corpus, embedding_array)
        )
        print(f"  💾 Sauvegardé")
    except Exception as e:
        print(f"❌ Erreur sauvegarde: {e}")

# EXÉCUTION
print("=" * 60)
print("PROTOTYPE RAG - EMBEDDINGS SIMULÉS")
print("=" * 60)

try:
    with psycopg2.connect(db_connection_str) as conn:
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute("""DROP TABLE IF EXISTS embeddings""")
            cur.execute("""CREATE TABLE embeddings (
                        ID SERIAL PRIMARY KEY, 
                        corpus TEXT,
                        embedding FLOAT8[]
                    )""")
            print("✅ Table créée")

            corpus_list = create_conversation_list(conversation_file_path)
            
            if corpus_list:
                for i, corpus in enumerate(corpus_list):
                    if corpus.strip():
                        print(f"[{i+1}/{len(corpus_list)}] {corpus[:50]}...")
                        embedding = calculate_embeddings(corpus)
                        save_embedding(corpus, embedding, cur)
                
                print(f"\n✅ {len(corpus_list)} embeddings sauvegardés!")
                
                # Vérification
                cur.execute("SELECT COUNT(*) FROM embeddings")
                count = cur.fetchone()[0]
                print(f"📊 Base de données: {count} enregistrements")

except Exception as e:
    print(f"❌ Erreur: {e}")