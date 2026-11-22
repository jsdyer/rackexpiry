export const day = d => /^\d{4}-\d{2}-\d{2}$/.test(d||'') && !Number.isNaN(Date.parse(d)) ? Math.floor(Date.parse(d+'T00:00:00Z')/86400000) : null;
export function matchCycle(product,version){
 const v=String(version).trim().replace(/^v/i,'');
 return [...(product?.releases||[])].sort((a,b)=>b.name.length-a.name.length).find(r=>v===r.name || (/^\d+(\.\d+)*$/.test(r.name)&&v.startsWith(r.name+'.'))) || null;
}
export function assess(product,version,today){
 const r=matchCycle(product,version); if(!r)return {status:'Unknown version',tone:'unknown',rank:4,release:null,days:null};
 const now=day(today),end=day(r.eolFrom?.slice(0,10)),active=day(r.eoasFrom?.slice(0,10)),days=end===null?null:end-now;
 if(day(r.releaseDate?.slice(0,10))!==null&&day(r.releaseDate.slice(0,10))>now)return {status:'Not released at assessment date',tone:'unknown',rank:4,release:r,days};
 let status='Support status unknown',tone='unknown',rank=4;
 if(end!==null?end<=now:r.isEol===true){status='Support ended';tone='ended';rank=0;}
 else if(days!==null&&days<=180){status='Due within 180 days';tone='due';rank=1;}
 else if(active!==null?active<=now:r.isEoas===true){status='Past active support';tone='maintenance';rank=2;}
 else if(r.isMaintained===true||r.isEol===false){status='Within support';tone='supported';rank=3;}
 return {status,tone,rank,release:r,days};
}
export function parseInventory(text){
 if(text.length>200000)throw new Error('Keep imports under 200 KB.');
 if(text.trim().startsWith('[')){const rows=JSON.parse(text);if(!Array.isArray(rows))throw new Error('Expected an inventory array');return validateRows(rows);}
 const table=[];let row=[],field='',quoted=false;
 for(let i=0;i<text.length;i++){const c=text[i];if(c==='"'){if(quoted&&text[i+1]==='"'){field+='"';i++;}else if(!field||quoted)quoted=!quoted;else throw new Error('Unexpected quote in CSV.');}else if(c===','&&!quoted){row.push(field.trim());field='';}else if((c==='\n'||c==='\r')&&!quoted){if(c==='\r'&&text[i+1]==='\n')i++;row.push(field.trim());if(row.some(Boolean))table.push(row);row=[];field='';}else field+=c;}
 if(quoted)throw new Error('Unclosed quote in CSV.');row.push(field.trim());if(row.some(Boolean))table.push(row);
 const header=table[0]?.map(s=>s.toLowerCase());let columns=[0,1,2];if(header?.includes('asset')&&header.includes('product')&&header.includes('version')){columns=['asset','product','version'].map(k=>header.indexOf(k));table.shift();}
 else if(table.some(r=>r.length!==3))throw new Error('Use asset,product,version columns or a named header.');
 return validateRows(table.map(r=>({asset:r[columns[0]],product:r[columns[1]],version:r[columns[2]]})));
}
export function validateRows(rows){if(rows.length>500)throw new Error('Maximum 500 inventory rows.');return rows.map(r=>{if(!r||!['asset','product','version'].every(k=>typeof r[k]==='string'&&r[k].trim()&&r[k].length<=160))throw new Error('Each row needs asset, product and version (up to 160 characters).');return {asset:r.asset.trim(),product:r.product.trim().toLowerCase(),version:r.version.trim()};});}
export function csv(rows){return rows.map(r=>r.map(v=>'"'+String(v??'').replace(/^[=+@-]/,"'$&").replaceAll('"','""')+'"').join(',')).join('\r\n');}
