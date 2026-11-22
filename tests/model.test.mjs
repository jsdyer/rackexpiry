import test from 'node:test';import assert from 'node:assert/strict';import {assess,matchCycle,parseInventory,csv} from '../web/model.mjs';
const p={releases:[{name:'22',isEol:false},{name:'22.04',eolFrom:'2027-05-01',eoasFrom:'2026-04-01',isMaintained:true},{name:'18',eolFrom:'2025-04-30',isEol:true}]};
test('longest cycle boundary avoids version 220 matching 22',()=>{assert.equal(matchCycle(p,'22.04.3').name,'22.04');assert.equal(matchCycle(p,'220'),null);});
test('end date has priority over stale API bool; same-day deadline is ended',()=>{assert.equal(assess(p,'22.04','2027-05-01').tone,'ended');assert.equal(assess(p,'22.04','2027-01-01').tone,'due');assert.equal(assess(p,'22.04','2026-04-02').tone,'maintenance');});
test('unknown versions never become supported',()=>assert.equal(assess(p,'23','2026-01-01').tone,'unknown'));
test('strict import stays atomic and rejects malformed oversized input',()=>{assert.equal(parseInventory('asset,product,version\na,php,8.5')[0].product,'php');assert.throws(()=>parseInventory('a,b'));assert.throws(()=>parseInventory('[{"asset":"x"}]'));});
test('CSV spreadsheet formulas are neutralized',()=>assert.ok(csv([['=cmd','hello"world']]).startsWith('"\'=cmd"')));

test('exported CSV with commas and extra evidence columns imports again',()=>{const x=csv([['asset','product','version','status'],['web, one','php','8.5','supported']]);assert.deepEqual(parseInventory(x),[{asset:'web, one',product:'php',version:'8.5'}]);});
