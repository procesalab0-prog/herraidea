(() => {
  class HerraideaSound {
    constructor() {
      this.enabled = localStorage.getItem('herraidea:sound') === 'on';
      this.context = null;
      this.master = null;
      this.button = document.querySelector('#sound-toggle');
      this.syncButton();
      this.button?.addEventListener('click', event => { event.stopPropagation(); this.toggle(); });
      document.addEventListener('click', event => {
        if (!this.enabled || event.target.closest('#sound-toggle,.brand')) return;
        if (event.target.closest('.family-toggle,[data-open-family]')) return;
        if (event.target.closest('button,.button,.product-card,.main-nav a,.section-head a')) this.play('button');
      }, true);
    }

    async init() {
      if (this.context) { if (this.context.state === 'suspended') await this.context.resume(); return; }
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      if (!AudioContext) return;
      this.context = new AudioContext();
      const compressor = this.context.createDynamicsCompressor();
      compressor.threshold.value = -18; compressor.knee.value = 18; compressor.ratio.value = 4;
      this.master = this.context.createGain(); this.master.gain.value = .16;
      this.master.connect(compressor); compressor.connect(this.context.destination);
      await this.context.resume();
    }

    async toggle() {
      this.enabled = !this.enabled;
      localStorage.setItem('herraidea:sound', this.enabled ? 'on' : 'off');
      this.syncButton();
      if (this.enabled) { await this.init(); this.play('unlock'); }
    }

    syncButton() {
      if (!this.button) return;
      this.button.classList.toggle('active', this.enabled);
      this.button.setAttribute('aria-pressed', String(this.enabled));
      this.button.setAttribute('aria-label', this.enabled ? 'Desactivar sonido' : 'Activar sonido');
      this.button.querySelector('span').textContent = this.enabled ? '♫' : '♩';
    }

    tone(freq, duration, gain = .18, type = 'sine', delay = 0, endFreq = freq) {
      if (!this.context || !this.master) return;
      const now = this.context.currentTime + delay;
      const osc = this.context.createOscillator(), amp = this.context.createGain();
      osc.type = type; osc.frequency.setValueAtTime(freq, now); osc.frequency.exponentialRampToValueAtTime(Math.max(20, endFreq), now + duration);
      amp.gain.setValueAtTime(.0001, now); amp.gain.exponentialRampToValueAtTime(gain, now + .012); amp.gain.exponentialRampToValueAtTime(.0001, now + duration);
      osc.connect(amp); amp.connect(this.master); osc.start(now); osc.stop(now + duration + .02);
    }

    noise(duration = .2, gain = .08, frequency = 1200, delay = 0) {
      if (!this.context || !this.master) return;
      const length = Math.ceil(this.context.sampleRate * duration), buffer = this.context.createBuffer(1, length, this.context.sampleRate), data = buffer.getChannelData(0);
      for (let i = 0; i < length; i++) data[i] = (Math.random() * 2 - 1) * (1 - i / length);
      const source = this.context.createBufferSource(), filter = this.context.createBiquadFilter(), amp = this.context.createGain(), now = this.context.currentTime + delay;
      source.buffer = buffer; filter.type = 'bandpass'; filter.frequency.value = frequency; filter.Q.value = 1.8;
      amp.gain.setValueAtTime(gain, now); amp.gain.exponentialRampToValueAtTime(.0001, now + duration);
      source.connect(filter); filter.connect(amp); amp.connect(this.master); source.start(now);
    }

    async play(name) {
      if (!this.enabled) return;
      await this.init();
      if (name === 'unlock') { this.tone(440,.2,.12,'sine'); this.tone(660,.28,.1,'sine',.1); }
      if (name === 'button') { this.tone(760,.055,.055,'triangle',0,520); }
      if (name === 'night') { this.noise(.9,.1,380); this.tone(82,1.15,.1,'sine',0,55); this.tone(164,.7,.045,'sine',.12,110); }
      if (name === 'metal') { this.tone(690,.075,.042,'triangle',0,510); this.tone(920,.055,.018,'sine',.018,720); }
      if (name === 'tags') { [0,.09,.18].forEach((d,i) => this.tone(880+i*110,.07,.04,'triangle',d,650+i*80)); }
      if (name === 'roulette') { [0,.045,.09].forEach((d,i) => this.tone(660+i*85,.038,.025-i*.004,'triangle',d,520+i*55)); }
      if (name === 'shipping') { this.tone(820,.065,.018,'sine',0,680); }
      if (name === 'easter') { [392,523,659,784].forEach((f,i) => this.tone(f,.34,.085,'sine',i*.11,f*1.01)); this.noise(.5,.045,2200,.25); }
    }
  }
  window.herraideaSound = new HerraideaSound();
})();
