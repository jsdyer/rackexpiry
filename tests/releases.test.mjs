import test from 'node:test';import assert from 'node:assert/strict';
import {compareStable,releaseStatus,parseReleaseWatch,matchCycle} from '../web/model.mjs';
test('stable ordering compares numbers, never lexical strings or abbreviated cycles',()=>{
assert.equal(compareStable('v8.5.10','8.5.9'),1);assert.equal(compareStable('6.5','v6.6'),-1);assert.equal(compareStable('8.5','8.5.1'),null);assert.equal(compareStable('1.0.0-ubuntu1','1.0.1'),null);assert.equal(compareStable('1.0.0-rc.1','1.0.0'),null);assert.equal(compareStable('9007199254740993.1','9007199254740992.2'),1);
assert.equal(releaseStatus('1.2.0','1.2.0'),'Matches recorded release');assert.equal(releaseStatus('1.1.0','1.2.0'),'Newer recorded release available');});
test('branch matching does not turn a newer major release into a same-branch update',()=>{
const p={releases:[{name:'8.4',latest:{name:'8.4.10'}},{name:'8.5',latest:{name:'8.5.1'}}]};const branch=matchCycle(p,'8.4.10');assert.equal(releaseStatus('8.4.10',branch.latest.name),'Matches recorded release');assert.equal(releaseStatus('8.4',branch.latest.name),'Exact version needs verification');});
test('application version backup strips unexpected fields and rejects duplicates/oversize',()=>{
assert.deepEqual(parseReleaseWatch([{id:'new-app',installed:' 1.2 ',url:'evil'}]),[{id:'new-app',installed:'1.2'}]);assert.throws(()=>parseReleaseWatch([{id:'x',installed:'1'},{id:'x',installed:'2'}]));assert.throws(()=>parseReleaseWatch(Array(101).fill({id:'x',installed:'1'})));assert.throws(()=>parseReleaseWatch([{id:'x',installed:''}]));});
