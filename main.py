#!/usr/bin/env python3
import os
import tkinter as tk
import wave
import threading
import random
devnull = os.open(os.devnull, os.O_WRONLY)
os.dup2(devnull, 2)
os.close(devnull)

window_size = {'width':650, 'height':450}#=ディスプレイ
default_style = {'anchor':'w', 'justify':'left'}
ff = 'Corbel'
QUESTION = ["HELLO", "HELL", "HELP", "SSO", "SOS", "FISH", "SELFISH", "APPLE", "ORANGE", "BANANA", "MORSE", "2026", "TRANSISTOR", "SPIELEN", "KINO", "KITAMI", "HOKKAIDO", "SYORIKEN", "PROGRAMING", "PYTHON", "NH3COOH", "DHMO", "BASO4", "SIO2", "GAUSS", "NEWTON", "BALL", "MATERIAL"]

#対応表を作る
MORS_MAP = ['ーーーーー','・ーーーー','・・ーーー','・・・ーー','・・・・ー','・・・・・','ー・・・・','ーー・・・','ーーー・・','ーーーー・',
'・ー','ー・・・','ー・ー・','ー・・','・','・・ー・','ーー・','・・・・','・・','・ーーー','ー・ー','・ー・・','ーー','ー・',
'ーーー','・ーー・','ーー・ー','・ー・','・・・','ー','・・ー','・・・ー','・ーー','ー・・ー','ー・ーー','ーー・・']
CHAR_MAP = ['0','1','2','3','4','5','6','7','8','9',
'A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
#モールス符号にする
def morse_encode(text):
	text = text.upper()
	result = ''
	l = len(MORS_MAP)
	encode_map = {}
	for i in range(l):
		encode_map[CHAR_MAP[i]] = MORS_MAP[i]
	for c in text:
		if c in CHAR_MAP:
			result += encode_map[c]
		else:
			result += c
		result += ' '
	return result.strip()
#解読する
def morse_decode(morse):
	result = ''
	l = len(MORS_MAP)
	decode_map = {}
	for i in range(l):
		decode_map[MORS_MAP[i]] = CHAR_MAP[i]
	mae = ''
	for m in morse.split(' '):
		if m in MORS_MAP:
			result += decode_map[m]
		elif m == '' and mae == '':
			result += ' '
		mae = m
	return result.strip()

is_key_enable = True
class Speak:
	def __init__(self, label_name, wrap_len=False, next_btn=False, next_place=False):
		self.label = label_name
		self.next_btn = next_btn
		self.saying = False
		self.next_place = next_place
		self.text = ""
		self.count = 0
		self.speed = 50
		if wrap_len == False:
			self.width = int(window_size["width"] *0.95)
		else:
			self.width = wrap_len
	def say(self, text=False):
		global is_key_enable
		self.saying = True
		is_key_enable = False
		if text != False:
			self.text = text
			if text == "":
				self.label.config(text="")
			elif self.next_btn != False and self.next_place != False:
				self.next_btn.place_forget()
		if self.count < len(self.text):
			self.count += 1
			self.label.config(text=self.text[0:self.count], wraplength=self.width)
			tim = self.speed
			if self.text[self.count -1] == "。":
				tim *= 10
			elif self.text[self.count -1] == "、":
				tim *= 5
			self.label.after(tim, self.say)
		else:
			self.stop_saying()
	def say_all(self):
		self.label.config(text=self.text, wraplength=self.width)
		self.stop_saying()
	def stop_saying(self):
		global is_key_enable
		if self.next_btn != False and self.next_place != False:
			self.next_btn.place(**self.next_place)
		self.saying = False
		is_key_enable = True
		self.count = 0
		self.text = ''
class Stage:
	__slots__ = ("SID_TITLE","SID_MAIN","SID_END","SID_BACK",
	"id","page","bg","memframe","time","pvar","description_list",
	"main_point","save_file","rank","head","next_link","question","ans")
	def __init__(self, root):
		#画面遷移
		self.SID_TITLE = 1
		self.SID_MAIN = 2
		self.SID_END = 3
		self.SID_BACK = 4
		self.rank = 0
		self.time = {}
		self.pvar = None
		self.head = None
		self.ans = None
		self.id = self.SID_TITLE #タイトル画面で初期化
		self.bg = "#043" #デフォルト背景色
		self.question = ""
		self.description_list = (
		"此の度は実行有難うございます。制作者のMikasaです。ここでは、此れの使い方等について説明します。",
		"Ctrl+Q: 終了\nEsc: タイトルに戻る\nEnter: 決定\nマウス:青色の文字はクリック出来ます",
		"ゲームの説明\nモールス符号を解読するゲームです。全ての問題が、何ら化の単語になっているので、分からない符号があっても諦めずに頑張ろう。次のページにヒントを載せます。見たくない人はEscキーで戻りましょう。",
		"答えとなりうる選択肢一覧:"+", ".join(QUESTION),
		"プレイ中は、問題の正解・不正解に関係なく、次の問題に進みます。正答を知ることは出来ません。自分で頑張りましょう。",
		"どうしても答えが知りたい方は、次へ進むと、見られます。見たくない人はEscキーで戻り魔性。",
		"答えと問題の組み合わせ:"+", ".join([morse_encode(i)+"=>"+i for i in QUESTION]),
		"それではおやすみなさい。\nー・ー",
		False)
		self.main_point = 0
		self.page = 0
		self.save_file = os.path.dirname(__file__)+"/save.dat"
		self.memframe = tk.Frame(root, bg=self.bg)
		self.reset()
	def reset(self):
		self.page = 0 #ページ移動(小さな画面遷移)
		self.time = {"t":0, "label":tk.Label(root), "limit":180}
	def save(self, point):
		r = []
		rank = 1
		if os.path.exists(self.save_file):
			isadd = False
			with open(self.save_file, "r") as f:
				t = f.readlines()
			for i in range(len(t)):
				t[i] = t[i].strip()
				if t[i].isdecimal():
					if isadd == False and int(t[i]) < point:
						r.append(str(point))
						isadd = True
					r.append(t[i])
					if isadd == False:
						rank += 1
			if isadd == False:
				r.append(str(point))
				rank = len(r)
		else:
			r.append(str(point))
		with open(self.save_file, "w") as f:
			f.write("\n".join(r)+"\n")
		self.rank = rank
	def moveStage(self, sid):
		self.id = sid
		self.reset()
		self.showWindow()
	def main_countup(self):
		if self.id == self.SID_MAIN:
			self.time["t"] += 1
			if self.time["t"] >= self.time["limit"]:
				self.save(self.main_point)
				self.moveStage(self.SID_END)
			else:
				self.showWindow(True)
				self.time["label"].after(1000, self.main_countup)
	def input_action(self, key):
		if is_key_enable:
			k = key.lower()
			if k == "quit":
				root.quit()
			elif self.id == self.SID_TITLE:
				if k == "return":
					self.moveStage(self.SID_MAIN)
				elif k == "space":
					self.moveStage(self.SID_BACK)
			elif self.id == self.SID_MAIN:
				if k == "escape":
					self.moveStage(self.SID_TITLE)
				elif self.page == 0 and k == "return":
					self.page += 1
					self.showWindow()
					self.main_countup()
				elif self.page != 0 and k == "return":
					if (morse_decode(self.question) == self.ans.get().strip().upper()):
						self.main_point += 1
					#連打長押し対策
					self.time["t"] += 1
					if self.time["t"] > self.time["limit"]:
						self.main_point = 0
						self.rank = 0
						self.moveStage(self.SID_TITLE)
					else:
						self.showWindow()
			elif self.id == self.SID_END:
				if k == "return":
					self.main_point = 0
					self.rank = 0
					self.moveStage(self.SID_TITLE)
			elif self.id == self.SID_BACK:
				if k == "return":
					self.page += 1
					if self.description_list[self.page] == False:
						self.moveStage(self.SID_TITLE)
					else:
						self.showWindow()
				elif k == "escape":
					self.moveStage(self.SID_TITLE)
	def showWindow(self, same=False):
		if not same:
			self.memframe.destroy()
		if self.id == self.SID_TITLE:
			self.memframe = tk.Frame(root, bg=self.bg)
			h1 = tk.Label(self.memframe, text="..-.-.-.--.-.-.---.-...", **default_style, bg=self.bg, fg="#fff", font=(ff, 35))
			description = tk.Label(self.memframe, **default_style, bg=self.bg, fg="#fff", font=(ff, 20))
			copy_right = tk.Label(self.memframe, text="© mikasa 2026", **default_style, bg=self.bg, fg="#fff", font=(ff, 20))
			links = []
			link_opt = ["スタート", "せつめい", "おしまい"]
			link_key = ["Return", "Space", "quit"]
			for i in range(3):
				links.append(tk.Label(self.memframe, text=link_opt[i], **default_style, bg=self.bg, fg="#15b", font=(ff, 30)))
			h1.place(relx=0, rely=0)
			copy_right.place(relx=0.3, rely=0.8)
			description.place(relx=0.1, rely=0.2)
			speak = Speak(description)
			speak.say("...............ようこそ......")
			for i in range(len(links)):
				links[i].bind("<Enter>", lambda e, j=i:links[j].config(font=(ff, 30, "bold")))
				links[i].bind("<Leave>", lambda e, j=i:links[j].config(font=(ff, 30)))
				links[i].bind("<Button-1>", lambda e, j=link_key[i]:self.input_action(j))
				links[i].place(relx=0.35, rely=0.4+0.1*i)
		elif self.id == self.SID_MAIN:
			if not same:
				self.memframe = tk.Frame(root, bg=self.bg)
				self.pvar = tk.Canvas(self.memframe, highlightthickness=0, width=0, height=10, background="#0ff")
				self.question = morse_encode(random.choice(QUESTION))
				self.ans = tk.Entry(self.memframe, width=25, font=(ff,25))
			else:
				self.pvar.config(width=window_size["width"]*(self.time["t"]/self.time["limit"]))
			if self.page == 0:
				self.head = tk.Label(self.memframe, **default_style, bg=self.bg, fg="#fff", font=(ff, 20))
				next_link = tk.Label(self.memframe, text="開始", **default_style, bg=self.bg, fg="#15b", font=(ff, 30))
				next_link.bind("<Enter>", lambda e, l=next_link:l.config(font=(ff, 30, "bold")))
				next_link.bind("<Leave>", lambda e, l=next_link:l.config(font=(ff, 30)))
				next_link.bind("<Button-1>", lambda e:self.input_action("Return"))
				speak = Speak(self.head, False, next_link, {"relx":0.5,"rely":0.6})
				self.head.place(relx=0, rely=0)
				speak.say("モールス符号が表示されます。解読してください。(大文字でも小文字でもどちらでもOK)\nエンターキーを押して開始、Escキーで中断します。")
				self.next_link = next_link
			else:
				if self.head != None:
					self.next_link.destroy()
					self.head.destroy()
					self.next_link = None
					self.head = None
				q = tk.Label(self.memframe, text="入力し終えたらエンターキーを押してね\n[問題]「"+self.question+"」\n以下の入力欄に回答を入れてね。", **default_style, bg=self.bg, fg="#fff", font=(ff, 20))
				q.place(relx=0,rely=0)
				self.ans.place(relx=0.3,rely=0.2)
				self.pvar.place(relx=0, rely=0.95)
				self.ans.focus()
		elif self.id == self.SID_END:
			self.memframe = tk.Frame(root, bg=self.bg)
			h1 = tk.Label(self.memframe, text="しゅーりょー(タイトルに戻るにはエンターキーを押してください) ", **default_style, bg=self.bg, fg="#fff", font=(ff, 30))
			rank = tk.Label(self.memframe, **default_style, bg=self.bg, fg="#fff", font=(ff, 20))
			rtext = f"得点: {self.main_point} 順位: {self.rank}位\n"
			with open(self.save_file, "r") as f:
				t = f.readlines()
			for i in range(min(len(t), 10)):
				t[i] = str(i+1)+"位 "+t[i]
			rtext += "".join(t[0:10])
			speak = Speak(rank)
			h1.place(relx=0, rely=0)
			rank.place(relx=0, rely=0.1)
			speak.say(rtext)
		elif self.id == self.SID_BACK:
			lbg = "#b30"
			self.memframe = tk.Frame(root, bg=lbg)
			h1 = tk.Label(self.memframe, text="くわしい説明", **default_style, bg=lbg, fg="#fff", font=(ff, 40))
			description = tk.Label(self.memframe, **default_style, bg=lbg, fg="#fff", font=(ff, 20))
			next_link = tk.Label(self.memframe, text="次へ", **default_style, bg=lbg, fg="#ff0", font=(ff, 30))
			speak = Speak(description, False, next_link, {"relx":0.5,"rely":0.8})
			h1.place(relx=0, rely=0)
			description.place(relx=0, rely=0.2)
			speak.say(self.description_list[self.page])
			next_link.bind("<Enter>", lambda e, l=next_link:l.config(font=(ff, 30, "bold")))
			next_link.bind("<Leave>", lambda e, l=next_link:l.config(font=(ff, 30)))
			next_link.bind("<Button-1>", lambda e:self.input_action("Return"))
			if self.description_list[self.page +1] == False:
				next_link.config(text="タイトルへ戻る")
		self.memframe.place(relx=0, rely=0, **window_size)

if __name__ == "__main__" and not("REQUEST_METHOD" in os.environ and os.environ["REQUEST_METHOD"]):
	root = tk.Tk()
	root.title("-.-. --.-")
	try:
		if os.path.exists(os.path.dirname(__file__)+"/favicon.ico"):
			root.iconbitmap(default=os.path.dirname(__file__)+"/favicon.ico")
	except:
		pass
	root.configure(background="#000")
	root.attributes("-fullscreen", True)
	# 画面サイズを取得
	window_size["width"] = root.winfo_screenwidth()
	window_size["height"] = root.winfo_screenheight()
	mainWindow = Stage(root)
	mainWindow.showWindow()
	root.bind('<Control-Key-q>', lambda x:mainWindow.input_action("quit"))
	root.bind("<KeyPress>", lambda event:mainWindow.input_action(event.keysym))
	root.mainloop()
