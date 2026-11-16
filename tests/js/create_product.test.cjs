const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const file = path.join(__dirname, '../../service/static/js/create_product.js');

function setup() {
    const elements = Object.fromEntries(['create-product-form', 'create-btn',
        'create_product_name', 'create_product_description', 'create_product_price']
        .map(id => [id, {value: '', disabled: true, listeners: {},
            addEventListener(event, handler) { this.listeners[event] = handler; }}]));
    elements.create_product_name.value = 'Notebook';
    elements.create_product_description.value = 'Paper';
    elements.create_product_price.value = '19.99';
    const calls = [], messages = [], shown = [], refreshes = [];
    let response = async () => ({status: 201, json: async () => ({
        id: 10, name: 'Notebook', description: 'Paper', price: '19.99'
    })});
    vm.runInNewContext(fs.readFileSync(file, 'utf8'), {
        document: {readyState: 'complete', getElementById: id => elements[id]},
        window: {ProductsUI: {API_BASE_URL: '/api/products', clearMessage() {},
            showMessage: (message, kind) => messages.push({message, kind}),
            showProductDetails: product => shown.push(product)},
            ProductsList: {loadProducts: async () => { refreshes.push(true); }}},
        fetch: async (...args) => { calls.push(args); return response(); }
    });
    return {elements, calls, messages, shown, refreshes, respond: fn => { response = fn; },
        submit: () => elements['create-product-form'].listeners.submit({preventDefault() {}})};
}

test('creates a product and displays its saved fields and ID', async () => {
    const s = setup();
    assert.equal(s.elements['create-btn'].disabled, false);
    await s.submit();
    assert.equal(s.calls[0][0], '/api/products');
    assert.equal(s.calls[0][1].method, 'POST');
    assert.deepEqual(JSON.parse(s.calls[0][1].body), {
        name: 'Notebook', description: 'Paper', price: '19.99'
    });
    assert.equal(s.shown[0].id, 10);
    assert.equal(s.messages.at(-1).kind, 'success');
    assert.equal(s.refreshes.length, 1);
});

test('accepts zero and an empty description', async () => {
    const s = setup();
    s.elements.create_product_price.value = '0';
    s.elements.create_product_description.value = '';
    await s.submit();
    assert.equal(JSON.parse(s.calls[0][1].body).price, '0');
    assert.equal(JSON.parse(s.calls[0][1].body).description, '');
});

test('invalid input sends no request', async () => {
    for (const [field, value] of [['name', ' '], ['name', 'x'.repeat(64)],
        ['price', ''], ['price', '-1'], ['price', 'Infinity'], ['price', 'abc']]) {
        const s = setup();
        s.elements['create_product_' + field].value = value;
        await s.submit();
        assert.equal(s.calls.length, 0);
        assert.equal(s.messages.at(-1).kind, 'error');
        assert.equal(s.shown.length, 0);
        assert.equal(s.refreshes.length, 0);
    }
});

test('failed requests preserve input and never display success', async () => {
    for (const response of [
        async () => ({status: 400, json: async () => ({message: 'Invalid product'})}),
        async () => ({status: 500, json: async () => { throw Error('Invalid JSON'); }}),
        async () => { throw Error('Network unavailable'); }
    ]) {
        const s = setup(); s.respond(response);
        await s.submit();
        assert.equal(s.messages.at(-1).kind, 'error');
        assert.equal(s.shown.length, 0);
        assert.equal(s.elements.create_product_name.value, 'Notebook');
        assert.equal(s.refreshes.length, 0);
        assert.equal(s.elements['create-btn'].disabled, false);
    }
});

test('ignores duplicate submissions while saving', async () => {
    const s = setup(); let release;
    s.respond(() => new Promise(resolve => { release = resolve; }));
    const pending = s.submit();
    await s.submit();
    assert.equal(s.calls.length, 1);
    assert.equal(s.elements['create-btn'].disabled, true);
    release({status: 201, json: async () => ({id: 10})});
    await pending;
    assert.equal(s.elements['create-btn'].disabled, false);
});
