(()=>{
 const root=document.querySelector('.mcp-access');if(!root)return;
 const english=()=>localStorage.getItem('lang')==='en';
 const update=()=>{root.querySelectorAll('[data-mcp-zh]').forEach(node=>{node.textContent=node.dataset[english()?'mcpEn':'mcpZh'];});document.getElementById('mcpCopyStatus').textContent='';};
 update();
 const language=document.getElementById('langBtn');
 if(language)new MutationObserver(update).observe(language,{childList:true,characterData:true,subtree:true});
 document.getElementById('mcpCopy').addEventListener('click',async()=>{
  const input=document.getElementById('mcpAddress'),status=document.getElementById('mcpCopyStatus');
  try{await navigator.clipboard.writeText(input.value);status.textContent=english()?'URL copied':'地址已复制';}
  catch{input.focus();input.select();status.textContent=english()?'Select and copy the URL above.':'请复制上方已选中的地址。';}
 });
})();
