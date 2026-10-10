'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const M = require('../game/v2/model.js');
test('original units and both market denominators reproduce 2.92 trillion servings and $116.8 billion', () => {
  const r=M.calculate(M.DEFAULTS);
  assert.equal(r.servings,2.92e12);
  assert.equal(r.profit,116.8e9);
  assert.equal(r.profit/1e8,1168);
  assert.equal(r.value,2.1024e12);
  assert.ok(Math.abs(r.neededMultiple-17.123287671232877)<1e-10);
});
test('one-factor stress scenarios distinguish profits from valuation', () => {
  const r=M.calculate(M.DEFAULTS);
  assert.equal(r.marginHalvedValue,1.0512e12);
  assert.equal(r.shareHalvedValue,1.0512e12);
  assert.equal(r.lowerMultipleValue,1.4016e12);
  assert.equal(M.calculate({...M.DEFAULTS,margin:2}).profit,58.4e9);
});
test('zero demand and zero margin have no infinite implied valuation', () => {
  for(const params of [{market:0},{share:0},{margin:0}]){
    const r=M.calculate({...M.DEFAULTS,...params});
    assert.equal(r.profit,0);assert.equal(r.value,0);assert.equal(r.neededMultiple,null);
  }
});
test('parameters are finite, bounded and respect native control increments', () => {
  assert.deepEqual(M.parameters({market:Infinity,share:'90',margin:null,multiple:NaN}),M.DEFAULTS);
  assert.deepEqual(M.parameters({market:101,share:-1,margin:3.1,multiple:48}),{market:100,share:0,margin:3,multiple:40});
});
test('all experiments check their actual prerequisites', () => {
  const a={...M.DEFAULTS},b={...a,margin:2},c={...a,multiple:12};
  assert.ok(M.MISSIONS[0].pass(a));assert.ok(!M.MISSIONS[1].pass(a));
  assert.ok(M.MISSIONS[1].pass(b));assert.ok(!M.MISSIONS[2].pass(b));assert.ok(M.MISSIONS[2].pass(c));
  assert.ok(!M.MISSIONS[0].pass({...a,share:25}));
});
test('final board preserves its declared decimal margin without slider rounding', () => {
  const r=M.simulate({product:3,brand:3,channel:4});
  assert.equal(r.margin,2.8);assert.equal(r.share,34);assert.equal(r.market,30);
  assert.ok(Math.abs(r.profit-r.servings*.028)<.001);
  assert.equal(r.value,r.profit*18);assert.ok(r.valid&&r.balanced);
});
test('every legal resource allocation reconciles to disclosed model rules', () => {
  for(let product=0;product<=10;product++) for(let brand=0;brand<=10-product;brand++){
    const channel=10-product-brand,r=M.simulate({product,brand,channel});
    assert.ok(r.valid);assert.equal(r.balanced,Math.min(product,brand,channel)>=2);
    const servings=8e9*8*365*r.market/100*r.share/100;
    assert.equal(r.servings,servings);assert.ok(Math.abs(r.profit-servings*r.margin/100)<.001);
    assert.ok(Number.isFinite(r.value));
  }
  assert.ok(!M.simulate({product:10,brand:10,channel:10}).valid);
  assert.ok(!M.simulate({product:2,brand:2,channel:2}).valid);
});
