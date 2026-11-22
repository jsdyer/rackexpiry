export function day(value){
 if(typeof value!=='string'||!/^\d{4}-\d{2}-\d{2}$/.test(value))return null;
 const ms=Date.parse(value+'T00:00:00Z');
 return Number.isFinite(ms)&&new Date(ms).toISOString().slice(0,10)===value?Math.floor(ms/86400000):null;
}
export function matchCycle(product,version){
 const v=String(version).trim().replace(/^v(?=\d)/i,'');
 const releases=[...(product?.releases||[])].sort((a,b)=>b.name.length-a.name.length);
 const exact=releases.find(r=>v.toLowerCase()===r.name.toLowerCase());if(exact)return exact;
 // A numeric prefix is safe only when the entire installed version is numeric.
 // Arbitrary text and prereleases must not inherit a stable branch's status.
 if(!/^\d+(?:\.\d+)*$/.test(v))return null;
 return releases.find(r=>/^\d+(?:\.\d+)*$/.test(r.name)&&v.startsWith(r.name+'.'))||null;
}
export function assess(product,version,today,observedOn){
 const r=matchCycle(product,version),unknown={status:'Unknown version',tone:'unknown',rank:4,release:r,days:null};
 if(!r)return unknown;
 const now=day(today),observed=day(observedOn?.slice(0,10));
 if(now===null)return {...unknown,status:'Choose a valid assessment date'};
 const date=value=>typeof value==='string'?day(value.slice(0,10)):null;
 const end=date(r.eolFrom),active=date(r.eoasFrom),released=date(r.releaseDate),days=end===null?null:end-now;
 if(released!==null&&released>now)return {...unknown,status:'Not released at assessment date',days};
 // Upstream Date.today > deadline means the published date is the final supported day.
 // A Boolean with no date is an observation at the catalogue check, not a forecast.
 const atObservation=observed!==null&&now===observed;
 if(end===null&&!atObservation)return {...unknown,status:'Support status unknown at assessment date',days};
 if(end!==null?now>end:r.isEol===true)return {status:'Support ended',tone:'ended',rank:0,release:r,days};
 if(end!==null&&days<=180)return {status:'Due within 180 days',tone:'due',rank:1,release:r,days};
 if(end===null&&r.isEol!==false)return {...unknown,status:'Support status unknown',days};
 if(active!==null?now>active:atObservation&&r.isEoas===true)return {status:'Past active support',tone:'maintenance',rank:2,release:r,days};
 // isMaintained can include paid extended support; it never establishes standard support.
 return {status:'Within support',tone:'supported',rank:3,release:r,days};
}
export function inventoryJson(rows){return JSON.stringify(validateRows(rows),null,2);}
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
