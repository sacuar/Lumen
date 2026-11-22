const Preview={
 path:null,page:0,generation:0,
 init(){for(const [id,fn] of [["preview-close",()=>this.close()],["preview-prev",()=>this.show(this.path,this.page-1)],["preview-next",()=>this.show(this.path,this.page+1)]])document.getElementById(id).onclick=fn;},
 close(){this.generation++;this.path=null;document.getElementById("preview-panel").hidden=true;},
 async show(path,page=0){const n=++this.generation;this.path=path;document.getElementById("preview-panel").hidden=false;const title=document.getElementById("preview-title"),body=document.getElementById("preview-content");title.textContent="Loading preview…";body.replaceChildren();
 try{const r=await API.post("/api/preview",{path,page});if(n!==this.generation)return;if(r.error)throw Error(r.error);this.page=r.page;title.textContent=r.name+" · Read only";const el=document.createElement(r.kind==="image"?"img":"pre");if(r.kind==="image")el.src=r.data;else el.textContent=r.data;body.append(el);document.getElementById("preview-count").textContent=(r.page+1)+" / "+r.pages;document.getElementById("preview-prev").disabled=r.page===0;document.getElementById("preview-next").disabled=r.page+1>=r.pages;}catch(e){if(n===this.generation)title.textContent=e.message;}
 }
};