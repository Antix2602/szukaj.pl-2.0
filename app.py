from flask import Flask, request, jsonify, render_template_string
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def scrape_duckduckgo(query, max_results=40):
    session = requests.Session()
    headers = {"User-Agent": "Mozilla/5.0"}
    url = "https://html.duckduckgo.com/html/"
    data = {"q": query}
    try:
        response = session.post(url, headers=headers, data=data, timeout=10)
        response.raise_for_status()
    except:
        return []
    soup = BeautifulSoup(response.text, "html.parser")
    results = []
    for r in soup.find_all("div", class_="result", limit=max_results):
        link_tag = r.find("a", class_="result__a")
        snippet_tag = r.find("a", class_="result__snippet")
        if link_tag:
            results.append({
                "title": link_tag.get_text(),
                "link": link_tag["href"],
                "snippet": snippet_tag.get_text() if snippet_tag else ""
            })
    return results

@app.route("/")
def home():
    html_content = """
<!DOCTYPE html>
<html lang="pl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Szukaj.pl 2.0</title>
<style>
body {
  margin:0; font-family:'Segoe UI', sans-serif;
  background:linear-gradient(-45deg,#0f2027,#203a43,#2c5364,#1f1c2c);
  background-size:400% 400%;
  color:white; min-height:100vh;
  display:flex; flex-direction:column; align-items:center; overflow-x:hidden;
  animation:gradientBG 15s ease infinite;
  perspective:1000px;
}
.container {
  margin-top:60px; width:90%; max-width:900px; text-align:center;
  animation:fadeIn 1s ease;
}
h1 {
  font-size:3.5rem; margin-bottom:30px;
  background:linear-gradient(to right,#ff416c,#ff4b2b,#ffb347,#ff7e5f);
  -webkit-background-clip:text; -webkit-text-fill-color:transparent;
  cursor:pointer; transition:transform 0.5s, text-shadow 0.3s;
  animation:headerPulse 2s infinite alternate;
}
h1:hover{
  transform:scale(1.2) rotate(-5deg);
  text-shadow:0 0 40px rgba(255,75,43,0.8);
}
.search-box{
  display:flex; justify-content:center; margin-bottom:30px;
  position:relative;
}
input[type=text]{
  width:70%; padding:16px 25px; border:none; border-radius:25px 0 0 25px;
  outline:none; font-size:1.2rem; transition:0.3s;
}
input[type=text]:focus{
  box-shadow:0 0 25px #ff416c; background:#fff; color:#222;
}
button{
  padding:16px 25px; border:none; border-radius:0 25px 25px 0;
  background:linear-gradient(45deg,#ff4b2b,#ff416c,#ffb347,#ff7e5f);
  color:white; cursor:pointer;
  overflow:hidden; position:relative; transition:0.4s, transform 0.2s;
  animation:buttonPulse 2s infinite alternate;
}
button:hover{
  transform:scale(1.1) rotate(-2deg);
}
.results{
  margin-top:40px; display:flex; flex-direction:column; width:100%;
}
.result-item{
  background:rgba(255,255,255,0.95); color:#222;
  padding:20px; border-radius:20px; margin-bottom:20px;
  opacity:0; transform:translateY(50px) rotateX(15deg) scale(0.95);
  animation:fadeSlide 0.8s forwards;
  transition:transform 0.4s, box-shadow 0.4s;
  position:relative;
}
.result-item:hover{
  transform:translateY(-5px) rotateX(0deg) scale(1.05);
  box-shadow:0 20px 40px rgba(0,0,0,0.25);
}
.result-item a{
  color:#1a0dab; font-size:1.3rem; font-weight:bold; text-decoration:none;
  transition:color 0.3s, text-shadow 0.3s;
}
.result-item a:hover{
  color:#ff416c; text-shadow:0 0 12px #ff416c;
}
.result-item p{
  margin-top:8px; font-size:1rem; color:#555;
  animation: pulse 2s infinite;
}
.theme-toggle{
  margin-top:20px; padding:10px 18px; border:none;
  border-radius:25px; cursor:pointer; background:#444; color:white;
  transition:0.3s, transform 0.2s;
}
.theme-toggle:hover{
  background:#666; transform:scale(1.05);
}
body.light{
  background:#f5f5f5; color:#222;
}
body.light .result-item{background:#fff; color:#222;}
body.light button{background:#4285f4;}
body.light button:hover{background:#357ae8;}
body.light h1{-webkit-text-fill-color:initial; background:none; color:#222;}
@keyframes gradientBG{
  0%{background-position:0% 50%;}
  50%{background-position:100% 50%;}
  100%{background-position:0% 50%;}
}
@keyframes fadeIn{from{opacity:0}to{opacity:1}}
@keyframes fadeSlide{to{opacity:1; transform:translateY(0) rotateX(0deg) scale(1);}}
@keyframes headerPulse{0%{text-shadow:0 0 10px rgba(255,75,43,0.6);}100%{text-shadow:0 0 40px rgba(255,75,43,0.9);}}
@keyframes buttonPulse{0%{box-shadow:0 0 15px rgba(255,65,108,0.5);}100%{box-shadow:0 0 40px rgba(255,65,108,0.8);}}
@keyframes pulse{0%,100%{opacity:0.8}50%{opacity:1;}}
</style>
</head>
<body>
<div class="container">
<h1 onclick="resetSearch()">Szukaj.pl 2.0</h1>
<div class="search-box">
<input type="text" id="searchInput" placeholder="Szukaj w internecie...">
<button onclick="performSearch(true)">🔍</button>
</div>
<button class="theme-toggle" onclick="toggleTheme()">🌙/☀️</button>
<div class="results" id="results"></div>
</div>
<script>
let input=document.getElementById("searchInput");
let resultsDiv=document.getElementById("results");
let offset=0;
let loading=false;
let currentQuery="";
async function performSearch(reset=true){
  if(loading) return;
  if(reset){ resultsDiv.innerHTML=""; offset=0; currentQuery=input.value.trim();}
  const query=currentQuery;
  if(!query) return;
  loading=true;
  try{
    const res=await fetch(`/search?q=${encodeURIComponent(query)}&offset=${offset}`);
    const data=await res.json();
    if(data.length===0 && offset===0){ resultsDiv.innerHTML=`<p>❌ Brak wyników dla "<b>${query}</b>"</p>`; loading=false; return;}
    data.forEach((item,index)=>{
      const div=document.createElement("div");
      div.classList.add("result-item");
      div.style.animationDelay=`${(offset+index)*0.05}s`;
      div.innerHTML=`<a href="${item.link}" target="_blank">${item.title}</a><p>${item.snippet}</p>`;
      resultsDiv.appendChild(div);
    });
    offset+=data.length;
  }catch{ if(offset===0) resultsDiv.innerHTML="<p>⚠️ Błąd pobierania wyników.</p>"; }
  loading=false;
}
window.addEventListener("scroll", ()=>{
  if(window.innerHeight + window.scrollY >= document.body.offsetHeight - 50){
    performSearch(false);
  }
});
function toggleTheme(){ document.body.classList.toggle("light"); }
function resetSearch(){ input.value=""; resultsDiv.innerHTML=""; offset=0; currentQuery=""; }
</script>
</body>
</html>
"""
    return render_template_string(html_content)

@app.route("/search")
def search():
    query = request.args.get("q","")
    offset = int(request.args.get("offset",0))
    if not query:
        return jsonify([])
    all_results = scrape_duckduckgo(query, max_results=40)
    return jsonify(all_results[offset:offset+10])

if __name__ == "__main__":
    app.run(debug=True)














