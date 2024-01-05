import tkinter as tk
import tkinter.messagebox as tkmsg
from tkinter.filedialog import askopenfilename
from azure.storage.blob import BlockBlobService
import os
import pymongo

#作成したCognitiveの関数を呼び出す
from CognitiveAPIs import recognizeFace


def insert_faceinfo(post):
    #接続するMongoDBのコレクション
    co = client.facedb.faces
    result = co.insert_one(post)
    #挿入した_idのObjectidをリターン
    return result.inserted_id


def update_faceinfo(obid, blobpath):
    #接続するMongoDBのコレクション
    co = client.facedb.faces
    q = {"_id": obid}
    post = {"$set": {"blob-path": blobpath}}
    co.update_one(q, post)


def upload_to_blob(e):
    #関数内でグローバル変数に値を代入したい場合は変数宣言時にglobalを付ける
    global img
    
    #ファイルダイアログ
    f_path = askopenfilename(filetypes=[("pngファイルのみ","*.png")],initialdir="c:\\temp")
    f_name = os.path.basename(f_path)
    r = tkmsg.askokcancel("askokcancel", "{}をblobにアップロードします。\nよろしいでしょうか？".format(f_name))
    
    if r:        
        #ラベルの値をconfigureメソッドで変更
        label1.configure(text=f_path)

        #imgは関数を出た後も変更した値を保持し、メインループで再描画される必要がある
        img = tk.PhotoImage(file=f_path)
        canvas1.create_image(0, 0, image=img, anchor=tk.NW)

        #blobとしてアップロード
        service.create_blob_from_path(container_name=c_name, blob_name=f_name, file_path=f_path)
        print("blobアップロード完了")

        #別途定義したFaceAPIの外部モジュール呼び出し
        face_list = recognizeFace(f_path)

        for face in face_list:
            #Cosmos DBにインサートした_idのObjectIDを拾う
            obid = insert_faceinfo(face)
            #拾ったObjectIDからサーチし、ドキュメントをアップデート（blobパスの挿入）
            update_faceinfo(obid, "{}\{}".format(c_name, f_name))

            #faceRectangleの描画
            x1 = face["faceRectangle"]["left"]
            y1 = face["faceRectangle"]["top"]
            x2 = x1 + face["faceRectangle"]["width"]
            y2 = y1 + face["faceRectangle"]["height"]
            canvas1.create_rectangle(x1, y1, x2, y2, outline="#ff0000", width=3, fill="red")
            canvas1.create_text(x1, y1, text="{}才".format(face["age"]),anchor=tk.NW, font=("", 14))
        
        print("CosmosDBインサート完了")
   
def quit_root(e):
    #rootウインドウの終了
    root.quit()

#Cosmos DBの接続アカウント
uri = 'mongodb://cosmosdb0706:vBItysu7nzcA5bzrb7L2wbnT9EbNTLiq0u7HnIKJjTI7dg6HmjYeYZqhv77kSWe9eKegqrr3mRJaVFoZKHVrCw==@cosmosdb0706.documents.azure.com:10255/?ssl=true&replicaSet=globaldb'
client = pymongo.MongoClient(uri)

#ストレージアカウントとキー
a_name = "blobiwatanagaaki"
a_key = "B9u4KYuMMTBNLxXfT3TTKyJeFGWLLVkZQny6tbg74ZiQOc4yXvsWrtOaD1FH3DRPYvJU+m0YGSbqi9Kr9Ajs7g=="

#コンテナ名
c_name = "img"

#Blobサービスへ接続
service = BlockBlobService(account_name=a_name, account_key=a_key)

#メインウインドの作成
root = tk.Tk()
root.title("Upload to Blob/CosmosDB")
root.geometry("600x600")

#ボタンを配置
button1 = tk.Button(root, text="Upload to Blob/Cosmos")
button1.place(x=10, y=20, width=150, height=30)
button1.bind("<Button-1>", upload_to_blob)

button2 = tk.Button(root, text="終了")
button2.place(x=440, y=20, width=150, height=30)
button2.bind("<Button-1>", quit_root)

#ラベルを配置
label1 = tk.Label(root, text="file name")
label1.place(x=160, y=20, width=150, height=30)

#600px * 650pxのCanvasを作成
canvas1 = tk.Canvas(root, width=600, height=600)
#Canvasを指定した場所に配置
canvas1.place(x=10, y=50)
#イメージの設定 デフォルトは(x, y)=(10, 50)が画像の中心。anchor=tk.NWで画像の左上を(x, y)=(10, 50)にする
img = tk.PhotoImage(file="C:\\temp\\blunk.png")
canvas1.create_image(0, 0, image=img, anchor=tk.NW)

#メインループ
root.mainloop()

#これ以降はコード無し。定義された関数はメインループから呼ばれる