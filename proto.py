# 
# imports
#
# system imports
import os
import glob
import pandas as pd
import sys
import pickle
# installed packages
import insightface
from insightface.app import FaceAnalysis
import kagglehub
import cv2
import numpy
import numpy as np
import tqdm
from numpy.linalg import norm

pd.set_option('display.max_columns', None)

#
# config
#
LFW_LOCAL_PATH="/home/gwilliams/.cache/kagglehub/datasets/jessicali9530/lfw-dataset/versions/4"
LFW_SUMMARY_CSV="data/lfw.csv"
MODEL_PACK_NAME = 'buffalo_l'
EMBEDDING_MODEL_PATH="/home/gwilliams/.insightface/models/buffalo_l/w600k_r50.onnx"

#
# Download dataset(s) as needed
#

#
# Download LFW
if os.path.exists(LFW_LOCAL_PATH):
    print("INFO: LFW dataset exists")
else:
    # Download latest version
    path = kagglehub.dataset_download("jessicali9530/lfw-dataset")
    print("INFO: Path to dataset files:", path)

#
# Process LFW dataset as needed
#
if os.path.exists(LFW_SUMMARY_CSV):
    print("INFO: LFW csv exists")
    lfw_df = pd.read_csv( LFW_SUMMARY_CSV )
else:
    # Create summary dataframe of LFW images
    img_top_dir = os.path.join(LFW_LOCAL_PATH, "lfw-deepfunneled/lfw-deepfunneled/")
    images_dirs = glob.glob( os.path.join( img_top_dir, "*" ) )
    items = []
    for person_id, img_dir in enumerate(images_dirs):
        person_name = os.path.basename(img_dir)
        imgs = glob.glob( os.path.join(img_dir, "*" ))
        for img in imgs:
            item = {'name': person_name, \
                    'person_id': person_id, \
                    'fname': os.path.basename(img),\
                    'fpath': img }
            items.append(item)
    lfw_df = pd.DataFrame(items)
    lfw_df.to_csv(LFW_SUMMARY_CSV)
    print("INFO: Wrote", LFW_SUMMARY_CSV)
print("INFO: LFW head->")  
print( lfw_df.head(20) )

#
# Create insightface app object 
# and cache model as needed for later
# 
app = FaceAnalysis(name=MODEL_PACK_NAME)
app.prepare(ctx_id=0)

#
# Produce embeddings as needed
#
if "embedding" in lfw_df.columns:
    print("INFO: embeddings column exists")
else:
    lfw_df.insert( len(lfw_df.columns), 'embedding', lfw_df.shape[0]*[ pickle.dumps(np.nan) ])
    #obj = np.array([1,2],dtype=object)
    #lfw_df['embedding'] = lfw_df['embedding'].astype(object)
    idx = lfw_df.columns.get_loc("embedding")
    print( idx, lfw_df.head(20) )

    for i in tqdm.tqdm(range(lfw_df.shape[0])):
        row = lfw_df.iloc[i]
        try:
            img = cv2.imread(row['fpath'])
            embedding = app.get(img)[0]['embedding']
            lfw_df.at[i,'embedding'] = pickle.dumps(embedding)
        except:
            print("ERROR: skipping embedding for img=", img, row['fpath'])

    print( lfw_df.head(20) )
    lfw_df.to_csv(LFW_SUMMARY_CSV)
    print("INFO: Wrote", LFW_SUMMARY_CSV)

#
# Produce threshold needed
#
def compute_sim( feat1, feat2):
    try:
        #feat1 = feat1.ravel()
        #feat2 = feat2.ravel()
        sim = np.dot(feat1, feat2) / (norm(feat1) * norm(feat2))
        return sim
    except:
        #print("feat",feat1,feat2)
        return -1.0
        
detector = insightface.model_zoo.get_model(EMBEDDING_MODEL_PATH)

# cache valid deserialized embeddings
valid_rows=[] # cache valid row ids
valid_embeddings=[] # cache valid embeddings
valid_person_ids=[] # cache valid person ids 
print("INFO: original total images", lfw_df.shape[0])
for idx in tqdm.tqdm( range( lfw_df.shape[0] ) ): 
    row = lfw_df.iloc[idx]
    _emb = eval( row['embedding'] )
    emb = pickle.loads(_emb)
    if type(emb) != type(np.array([0])):
        continue
    valid_rows.append(idx)
    valid_person_ids.append(row['person_id'])
    valid_embeddings.append(emb)
print("INFO: total valid embeddings", len(valid_embeddings))

obj = {"rows": valid_rows, "person_ids": valid_person_ids, "embeddings": valid_embeddings }
f = open("data/valid_data.pkl","wb")
pickle.dump(obj,f)
f.flush()
f.close()
print("INFO: wrote valid data pkl")

# compute accuracies
total = 0
valid_total = 0
top_1 = 0
top_10 = 0
top_50 = 0
single = 0
match_scores=[]
first_nomatch_scores=[]
nomatch_scores=[]

# iterate all valid images
for a in tqdm.tqdm( range(len(valid_rows)) ):
    query_idx = valid_rows[a]
    query_row = lfw_df.iloc[query_idx]
    query_name = query_row['name']
    query_person_id = valid_person_ids[a]
    query_embedding = valid_embeddings[a]
    # produce score of query image with valid gallery images
    scores = []
    for b in range(len(valid_rows)):
        target_embedding = valid_embeddings[b]
        scores.append( compute_sim( query_embedding, target_embedding ) )
    n_scores = np.array(scores)
    scores_sorted = np.argsort(n_scores)[::-1]
    n_person_ids = np.array(valid_person_ids)
    persons_similar = n_person_ids[ scores_sorted ]
    # sanity check - we expected high similarity with query against itself in the gallery
    if persons_similar[0] != query_person_id: 
        print("ERROR: Sanity check failed at", query_idx, query_person_id, query_name, persons_similar[0])
        sys.exit(1)
    total += 1
    # check face has enough images
    num_occ = (n_person_ids == query_person_id ).sum()
    if num_occ ==0:
        print("ERROR: Invalid person occurrence=0", query_person_id)
        sys.exit(1)
    elif num_occ ==1:
        #print("WARNING: Not enough face images for person_id=", query_person_id )
        single += 1
        continue
    valid_total += 1
    # top 1
    if persons_similar[1] == query_person_id:
        top_1 += 1
        # track all matching scores
        match_scores.append( (n_scores[ scores_sorted[1] ], query_person_id, query_idx, valid_rows[ scores_sorted[1] ] ) )
        # locate first non-match
        #print("score track", persons_similar[0:10])
        for k in range(2, persons_similar.shape[0]+1):
            if persons_similar[k] == query_person_id:
                #print("top 1 match",k)
                continue
            else:
                # track the unmatch score
                #print("top 1 first unmatch",k)
                first_nomatch_scores.append( (n_scores[ scores_sorted[k] ], query_person_id, query_idx, valid_rows[ scores_sorted[k] ] ) )
                break
    else:
        nomatch_scores.append( ( n_scores[ scores_sorted[1] ], query_person_id, query_idx, valid_rows[ scores_sorted[1] ] ) )
    # top 10
    if query_person_id in persons_similar[1:10]:
        top_10 += 1
    # top 50
    if query_person_id in persons_similar[1:50]:
        top_50 += 1
    print("top_1=", top_1*1.0/valid_total, "top_10=", top_10*1.0/valid_total)
    print("single=%d/%d=" % (single, total), single*1.0/total)
    #print("match scores (%d)=" % len(match_scores), numpy.array(sorted(match_scores)))
    #print("first nomatch scores (%d)"% len(first_nomatch_scores), numpy.array(sorted(first_nomatch_scores)))
    #print("nomatch scores (%d)" % len(nomatch_scores), numpy.array(sorted(nomatch_scores)))

obj = { "match_scores": match_scores, "first_nomatch_scores":first_nomatch_scores,"nomatch_scores":nomatch_scores }
f = open("data/match_stats.pkl","wb")
pickle.dump(obj,f)
f.flush()
f.close()
print("INFO: Wrote score stats pkl")
 
print("Done.")
