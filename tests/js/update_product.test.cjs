// Run: node --test tests/js/update_product.test.cjs
const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const source = fs.readFileSync(path.join(__dirname, '../../service/static/js/update_product.js'), 'utf8');

function setup() {
    const ids = ['products_body', 'update-product-form', 'update-product-dialog',
        'update-btn', 'product_name', 'product_description', 'product_price'];
    const elements = Object.fromEntries(ids.map(id => [id, {
        value: '', dataset: {}, listeners: {}, disabled: false,
        addEventListener(event, fn) { this.listeners[event] = fn; }
    }]));
    elements['update-product-dialog'].dataset.productId = '7';
    elements.product_name.value = 'New name';
    elements.product_description.value = 'New description';
    elements.product_price.value = '24.50';
    const calls = [], messages = [], opened = [], saved = [];
    const rowName = {};
    elements['product-7'] = {cells: [{}, {}, {}, {}], querySelector: () => rowName};
    let response = async () => ({ok: true, json: async () => ({
        id: 7, name: 'New name', description: 'New description', price: '24.50'
    })});
    vm.runInNewContext(source, {
        document: {readyState: 'complete', getElementById: id => elements[id]},
        window: {ProductsUI: {
            API_BASE_URL: '/api/products', clearMessage() {},
            showMessage: (text, kind) => messages.push({text, kind}),
            openUpdateDialog: product => opened.push(product),
            updateForm: product => saved.push(product)
        }},
        fetch: async (...args) => { calls.push(args); return response(); }
    });
    return {elements, calls, messages, opened, saved, rowName,
        respond: fn => { response = fn; },
        submit: () => elements['update-product-form'].listeners.submit({preventDefault() {}}),
        open: button => elements.products_body.listeners.click({target: {closest: () => button}})};
}

test('loads a fresh product using the shared API path before opening the dialog', async () => {
    const s = setup();
    const button = {dataset: {productId: '7'}, disabled: false};
    await s.open(button);
    assert.equal(s.calls[0][0], '/api/products/7');
    assert.equal(s.opened[0].id, 7);
    assert.equal(button.disabled, false);
});

test('sends only editable fields, preserves decimal text and updates the displayed row', async () => {
    const s = setup();
    await s.submit();
    assert.equal(s.calls[0][0], '/api/products/7');
    assert.equal(s.calls[0][1].method, 'PUT');
    assert.deepEqual(JSON.parse(s.calls[0][1].body), {
        name: 'New name', description: 'New description', price: '24.50'
    });
    assert.equal(s.rowName.textContent, 'New name');
    assert.equal(s.elements['product-7'].cells[3].textContent, '24.50');
    assert.equal(s.messages.at(-1).kind, 'success');
});

test('rejects invalid values without sending a request', async () => {
    for (const [field, value] of [['product_name', '   '], ['product_name', 'x'.repeat(64)],
        ['product_price', '-1'], ['product_price', ''], ['product_price', 'NaN'],
        ['product_price', 'Infinity']]) {
        const s = setup();
        s.elements[field].value = value;
        await s.submit();
        assert.equal(s.calls.length, 0);
        assert.equal(s.messages.at(-1).kind, 'error');
    }
});

test('accepts a zero price', async () => {
    const s = setup(); s.elements.product_price.value = '0';
    await s.submit();
    assert.equal(JSON.parse(s.calls[0][1].body).price, '0');
});

test('404 and server validation errors never report success or change the row', async () => {
    for (const status of [400, 404]) {
        const s = setup();
        s.respond(async () => ({ok: false, status, json: async () => ({message: 'Invalid data'})}));
        await s.submit();
        assert.equal(s.messages.at(-1).kind, 'error');
        if (status === 404) assert.match(s.messages.at(-1).text, /not found/);
        assert.equal(s.saved.length, 0);
        assert.equal(s.rowName.textContent, undefined);
        assert.equal(s.elements['update-btn'].disabled, false);
    }
});

test('network and non-JSON failures restore the save button', async () => {
    for (const response of [async () => { throw Error('Network unavailable'); },
        async () => ({json: async () => { throw Error('Invalid JSON'); }})]) {
        const s = setup(); s.respond(response);
        await s.submit();
        assert.equal(s.messages.at(-1).kind, 'error');
        assert.equal(s.elements['update-btn'].disabled, false);
    }
});

test('prevents duplicate saves while the first request is pending', async () => {
    const s = setup(); let release;
    s.respond(() => new Promise(resolve => { release = resolve; }));
    const pending = s.submit();
    await s.submit();
    assert.equal(s.calls.length, 1);
    assert.equal(s.elements['update-btn'].disabled, true);
    release({ok: true, json: async () => ({id: 7, name: 'Saved', price: '0'})});
    await pending;
    assert.equal(s.elements['update-btn'].disabled, false);
});
