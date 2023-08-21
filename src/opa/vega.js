import { html, css, LitElement } from 'https://cdn.jsdelivr.net/gh/lit/dist@2/core/lit-core.min.js';
export class VegaGraph extends LitElement {
    static properties = {
        tickers: { type: Array },
        kinds: { type: Array },
        _kind: { type: String, state: true },
        _ticker: { type: String, state: true },
        _dataSetName: { state: true },
        _view: { state: true }
    };

    constructor() {
        super();
        this.tickers = JSON.parse(this.getAttribute("tickers"));
        this._ticker = this.tickers[0];

        this.kinds = JSON.parse(this.getAttribute("kinds"));
        this._kind = this.kinds[0];

        this.replaceGraph();
    }

    createRenderRoot() {
        return this;
    }

    dataUrl() {
        return `/json/${this._ticker}?kind=${this._kind}`
    }

    replaceGraph() {
        var self = this;
        fetch(this.dataUrl()).then(resp => {
            resp.json().then(json => {
                vegaEmbed(this.renderRoot.querySelector('#vega'), json).then(function (result) {
                    self._view = result.view
                    self._dataSetName = json.data.name
                }).catch(console.error);
            }).catch(console.error);
        });
    }

    updateGraph() {
        var self = this;
        fetch(this.dataUrl()).then(resp => {
            resp.json().then(json => {
                var changeSet = vega.changeset().remove(() => true).insert(json.datasets[json.data.name]);
                self._view.change(this._dataSetName, changeSet).run();
            })
        });
    }

    _changeTicker(e) {
        this._ticker = e.target.value;
        this.updateGraph();
    }

    _changeKind(e) {
        this._kind = e.target.value;
        this.replaceGraph();
    }

    render() {
        return html`
      <label for="select-ticker">Choose a ticker:</label>
  
      <select name="tickers" id="select-ticker" @change="${this._changeTicker}">
        ${this.tickers.map((t) =>
            html`<option value="${t}" ?selected=${this._ticker == t}>${t}</option>`
        )}
      </select>
  
      <label for="select-kind">Choose a data kind:</label>
  
      <select name="kinds" id="select-kind" @change="${this._changeKind}">
        ${this.kinds.map((k) =>
            html`<option value="${k}" ?selected=${this._kind == k}>${k}</option>`
        )}
      </select>

      <div id="vega"></div>
      `;
    }
}
customElements.define('vega-graph', VegaGraph);