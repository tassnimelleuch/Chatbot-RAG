# faire les importations nécessaires
import psycopg2
import numpy as np
import os
from pathlib import Path

# Déclarer les variables nécessaires
data_folder_path = "../data/DISTRIBUTION_ACCUEIL_UBS/TRANS_TXT/"
print(f"Dossier des conversations: {data_folder_path}")

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
    return embedding

def save_embedding(corpus: str, embedding: list[float], filename: str, cursor) -> None:
    """Sauvegarde dans PostgreSQL"""
    try:
        embedding_array = "{" + ",".join(str(x) for x in embedding) + "}"
        cursor.execute(
            '''INSERT INTO embeddings (corpus, embedding, source_file) VALUES (%s, %s, %s)''', 
            (corpus, embedding_array, filename)
        )
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
                        embedding FLOAT8[],
                        source_file TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )""")
            print("✅ Table créée")

            # Récupérer tous les fichiers .txt du dossier
            txt_files = list(Path(data_folder_path).glob("*.txt"))
            
            if not txt_files:
                print(f"❌ Aucun fichier .txt trouvé dans {data_folder_path}")
            else:
                print(f"\n📁 {len(txt_files)} fichiers trouvés\n")
                
                total_embeddings = 0
                
                for file_idx, file_path in enumerate(txt_files, 1):
                    filename = file_path.name
                    print(f"{'='*60}")
                    print(f"📄 [{file_idx}/{len(txt_files)}] Traitement: {filename}")
                    print(f"{'='*60}")
                    
                    corpus_list = create_conversation_list(str(file_path))
                    
                    if corpus_list:
                        for i, corpus in enumerate(corpus_list):
                            if corpus.strip():
                                print(f"  [{i+1}/{len(corpus_list)}] {corpus[:50]}...")
                                embedding = calculate_embeddings(corpus)
                                save_embedding(corpus, embedding, filename, cur)
                                total_embeddings += 1
                        
                        print(f"✅ {len(corpus_list)} embeddings sauvegardés depuis {filename}\n")
                
                print(f"{'='*60}")
                print(f"🎉 TRAITEMENT TERMINÉ")
                print(f"{'='*60}")
                print(f"📊 Total: {total_embeddings} embeddings depuis {len(txt_files)} fichiers\n")
                
                # Vérification finale
                cur.execute("SELECT COUNT(*) FROM embeddings")
                count = cur.fetchone()[0]
                
                cur.execute("SELECT source_file, COUNT(*) FROM embeddings GROUP BY source_file ORDER BY source_file")
                file_stats = cur.fetchall()
                
                print(f"📊 STATISTIQUES DE LA BASE DE DONNÉES:")
                print(f"   Total enregistrements: {count}")
                print(f"\n   Répartition par fichier:")
                for file, cnt in file_stats:
                    print(f"   - {file}: {cnt} embeddings")

except Exception as e:
    print(f"❌ Erreur: {e}")