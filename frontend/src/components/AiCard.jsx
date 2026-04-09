import React, { useState, useEffect, useRef } from 'react';

const OPENROUTER_API_KEY = import.meta.env.VITE_OPENROUTER_API_KEY;

const VAD_THRESHOLD_START = 0.012;
const VAD_THRESHOLD_STOP  = 0.008;
const VAD_SILENCE_MS      = 1400;
const VAD_MIN_SPEECH_MS   = 250;

const cssStyles = `
/* ══ Voice Card Container ══ */
.container-ai-voice {
  position: absolute;
  left: 0; right: 0; top: 0; bottom: 0;
  width: 100vw;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  gap: 20px;
  overflow: hidden;
  background-color: #f8f9fa;
}

.card {
  width: 12rem;
  height: 12rem;
  flex-shrink: 0;
  position: relative;
  transform-style: preserve-3d;
  will-change: transform;
  transition: all 0.6s ease;
  border-radius: 3rem;
  display: flex;
  align-items: center;
  transform: translateZ(50px);
  justify-content: center;
}

.card:hover {
  box-shadow:
    0 10px 40px rgba(0, 0, 60, 0.25),
    inset 0 0 10px rgba(255, 255, 255, 0.5);
}

.background-blur-balls {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translateX(-50%) translateY(-50%);
  width: 100%;
  height: 100%;
  z-index: -10;
  border-radius: 3rem;
  transition: all 0.3s ease;
  background-color: rgba(255, 255, 255, 0.8);
  overflow: hidden;
}
.balls {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translateX(-50%) translateY(-50%);
  animation: rotate-background-balls 10s linear infinite;
}

.container-wrap:hover .balls {
  animation-play-state: paused;
}

.background-blur-balls .ball {
  width: 6rem;
  height: 6rem;
  position: absolute;
  border-radius: 50%;
  filter: blur(30px);
}

.background-blur-balls .ball.violet {
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  background-color: #9147ff;
}

.background-blur-balls .ball.green {
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  background-color: #34d399;
}

.background-blur-balls .ball.rosa {
  top: 50%;
  left: 0;
  transform: translateY(-50%);
  background-color: #ec4899;
}

.background-blur-balls .ball.cyan {
  top: 50%;
  right: 0;
  transform: translateY(-50%);
  background-color: #05e0f5;
}

.content-card {
  width: 12rem;
  height: 12rem;
  display: flex;
  border-radius: 3rem;
  transition: all 0.3s ease;
  overflow: visible;
}

.background-blur-card {
  width: 100%;
  height: 100%;
  backdrop-filter: blur(50px);
  border-radius: 3rem;
  overflow: visible;
  position: relative;
}

.eyes {
  position: absolute;
  left: 50%;
  bottom: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  justify-content: center;
  height: 52px;
  gap: 2rem;
  transition: all 0.3s ease;
}

.eyes .eye {
  width: 26px;
  height: 52px;
  background-color: #fff;
  border-radius: 16px;
  animation: animate-eyes 10s infinite linear;
  transition: all 0.3s ease;
}

.eyes.happy {
  display: none;
  color: #fff;
  gap: 0;
}

.eyes.happy svg {
  width: 60px;
}

@keyframes rotate-background-balls {
  from {
    transform: translateX(-50%) translateY(-50%) rotate(360deg);
  }
  to {
    transform: translateX(-50%) translateY(-50%) rotate(0);
  }
}

/* ── Sleeping state ── */
.eyes.hidden {
  display: none !important;
}

.card.sleeping .balls {
  animation-play-state: paused;
}

.eyes.sleeping-eyes {
  position: absolute;
  left: 50%;
  bottom: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  justify-content: center;
  height: 52px;
  gap: 2rem;
}

.eye-closed {
  width: 26px;
  height: 6px;
  background-color: #fff;
  border-radius: 10px;
  position: relative;
  /* drooping lid curve */
  border-bottom-left-radius: 30px;
  border-bottom-right-radius: 30px;
  border-top-left-radius: 4px;
  border-top-right-radius: 4px;
}

/* Zzz floating animation */
.zzz-container {
  position: absolute;
  top: -10px;
  right: -36px;
  display: flex;
  flex-direction: column-reverse;
  align-items: flex-start;
  gap: 2px;
  pointer-events: none;
}

.zzz {
  color: #fff;
  font-weight: 700;
  font-family: sans-serif;
  opacity: 0;
  animation: floatZzz 2.4s ease-in-out infinite;
  text-shadow: 0 0 6px rgba(255,255,255,0.6);
}

.zzz.z1 { font-size: 18px; animation-delay: 0s; }
.zzz.z2 { font-size: 13px; animation-delay: 0.6s; }
.zzz.z3 { font-size: 9px;  animation-delay: 1.2s; }

@keyframes floatZzz {
  0%   { opacity: 0;   transform: translate(0, 0)   scale(0.7); }
  20%  { opacity: 1;   transform: translate(2px, -6px) scale(1); }
  80%  { opacity: 0.8; transform: translate(6px, -18px) scale(1.1); }
  100% { opacity: 0;   transform: translate(10px, -28px) scale(0.8); }
}

@keyframes animate-eyes {
  46% {
    height: 52px;
  }
  48% {
    height: 20px;
  }
  50% {
    height: 52px;
  }
  96% {
    height: 52px;
  }
  98% {
    height: 20px;
  }
  100% {
    height: 52px;
  }
}

/* ══════════════════════════════════════════
   THINKING EXPRESSION
   ══════════════════════════════════════════ */

.card.thinking {
  animation: thinkingBreath 2.2s ease-in-out infinite;
}
@keyframes thinkingBreath {
  0%, 100% { transform: translateZ(50px) scale(1); }
  50%       { transform: translateZ(50px) scale(1.025); }
}

/* Anchor: sits at the same vertical position as the normal eyes */
.thinking-face {
  position: absolute;
  left: 50%;
  bottom: 50%;
  transform: translateX(-50%);
  display: flex;
  flex-direction: column;
  align-items: center;
}

.thinking-eyes {
  display: flex;
  align-items: center;
  gap: 2rem;
  transform: translateY(-6px); /* look upward */
}

.thinking-eye {
  width: 26px;
  height: 18px;                /* squashed — half-open */
  background-color: #fff;
  border-radius: 16px;
  /* clip the bottom half to make a "looking up" lid shape */
  clip-path: inset(0 0 30% 0 round 16px);
  transition: all 0.3s ease;
}

.thinking-eye.eye-left  { transform: rotate(-6deg) translateX(-2px); }
.thinking-eye.eye-right { transform: rotate(6deg)  translateX(2px); }

/* subtle wobble while thinking */
.thinking-eyes {
  animation: thinkingWobble 3s ease-in-out infinite;
}
@keyframes thinkingWobble {
  0%, 100% { transform: translateY(-6px) rotate(0deg); }
  30%       { transform: translateY(-8px) rotate(-1.5deg); }
  60%       { transform: translateY(-5px) rotate(1deg); }
}

/* ── Thought bubble — floats ABOVE the card ── */
.thought-bubble {
  position: absolute;
  bottom: 100%;
  left: 52%;
  margin-bottom: 12px;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 5px;
  pointer-events: none;
  animation: bubbleFloat 2.4s ease-in-out infinite;
  z-index: 100;
}

@keyframes bubbleFloat {
  0%, 100% { transform: translateY(0); }
  50%       { transform: translateY(-5px); }
}

.thought-dot {
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.92);
  box-shadow: 0 2px 6px rgba(0, 0, 60, 0.15);
  animation: thoughtPulse 1.8s ease-in-out infinite;
  align-self: flex-start;
}
.td1 { width: 5px;  height: 5px;  margin-left: 4px;  animation-delay: 0.4s; }
.td2 { width: 8px;  height: 8px;  margin-left: 8px;  animation-delay: 0.2s; }
.td3 { width: 11px; height: 11px; margin-left: 12px; animation-delay: 0s;   }

@keyframes thoughtPulse {
  0%, 100% { opacity: 0.55; transform: scale(0.88); }
  50%       { opacity: 1;    transform: scale(1.12); }
}

.thought-cloud {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 999px;
  padding: 9px 16px;
  box-shadow:
    0 8px 24px rgba(0, 0, 60, 0.18),
    0 2px 6px rgba(145, 71, 255, 0.12),
    inset 0 1px 0 rgba(255,255,255,1);
  display: flex;
  align-items: center;
  gap: 6px;
  white-space: nowrap;
}

.cloud-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: linear-gradient(135deg, #9147ff, #3b82f6);
  animation: cloudDotBounce 1.1s ease-in-out infinite;
}
.cloud-dot:nth-child(1) { animation-delay: 0s;    }
.cloud-dot:nth-child(2) { animation-delay: 0.18s; }
.cloud-dot:nth-child(3) { animation-delay: 0.36s; }

@keyframes cloudDotBounce {
  0%, 100% { transform: translateY(0);    opacity: 0.35; }
  50%       { transform: translateY(-5px); opacity: 1;    }
}

/* ══════════════════════════════════════════
   PANELS — portalled to <body>, free from card clipping
   ══════════════════════════════════════════ */

.btns-add button.btn-active {
  color: #9147ff !important;
}

.floating-panel {
  position: fixed;
  width: 280px;
  background: #ffffff;
  border-radius: 20px;
  box-shadow:
    0 24px 64px rgba(0, 0, 60, 0.18),
    0 4px 16px rgba(145, 71, 255, 0.14),
    inset 0 1px 0 rgba(255,255,255,0.9);
  padding: 18px;
  z-index: 9999999;
  transform: translateY(-100%) translateY(-14px);
  animation: panelIn 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
  font-family: sans-serif;
}

@keyframes panelIn {
  from { opacity: 0; transform: translateY(-100%) translateY(-6px) scale(0.94); }
  to   { opacity: 1; transform: translateY(-100%) translateY(-14px) scale(1); }
}

/* ── Panel internals ── */
.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
  font-weight: 700;
  color: #333;
  margin-bottom: 14px;
  letter-spacing: -0.01em;
}

.panel-close {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f0f0f0;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  color: #888;
  font-size: 11px;
  transition: all 0.15s;
  flex-shrink: 0;
}
.panel-close:hover { background: #e0e0e0; color: #333; }

.panel-hint {
  font-size: 11px;
  color: #aaa;
  margin: -8px 0 12px;
  line-height: 1.5;
}

.panel-status {
  font-size: 11px;
  color: #9147ff;
  margin-top: 10px;
  text-align: center;
  font-weight: 500;
}

/* ── Drop zone (attach) ── */
.drop-zone {
  border: 2px dashed #e0e0e0;
  border-radius: 14px;
  padding: 28px 16px;
  text-align: center;
  cursor: pointer;
  transition: border-color 0.2s, background 0.2s;
  background: #fafafa;
}
.drop-zone:hover,
.drop-zone.dragging {
  border-color: #9147ff;
  background: #f5f0ff;
}
.drop-icon {
  font-size: 32px;
  display: block;
  margin-bottom: 8px;
}
.drop-zone p {
  margin: 0;
  font-size: 12px;
  color: #555;
  font-weight: 500;
}
.drop-hint {
  color: #bbb !important;
  font-size: 10px !important;
  margin-top: 5px !important;
  font-weight: 400 !important;
}

/* ── Apps grid ── */
.apps-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}

.app-chip {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
  padding: 12px 6px;
  border: 1.5px solid #eee;
  border-radius: 14px;
  background: #fafafa;
  cursor: pointer;
  font-size: 11px;
  font-weight: 500;
  color: #555;
  transition: all 0.15s;
}
.app-chip:hover {
  border-color: #9147ff;
  background: #f5f0ff;
  color: #7c3aed;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(145, 71, 255, 0.15);
}
.app-emoji { font-size: 22px; line-height: 1; }

/* ── App input area ── */
.app-input-area {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.back-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 11px;
  color: #9147ff;
  padding: 0;
  text-align: left;
  font-weight: 500;
  opacity: 0.8;
}
.back-btn:hover { opacity: 1; text-decoration: underline; }

.app-label {
  font-size: 13px;
  font-weight: 700;
  color: #333;
  margin: 0;
}
.app-textarea {
  width: 100%;
  height: 100px;
  border: 1.5px solid #eee;
  border-radius: 12px;
  padding: 10px 12px;
  font-size: 12px;
  color: #444;
  resize: none;
  outline: none;
  box-sizing: border-box;
  transition: border-color 0.2s;
  background: #fafafa;
  line-height: 1.5;
}
.app-textarea:focus { border-color: #9147ff; background: #fff; }
.app-textarea::placeholder { color: #ccc; }

.confirm-btn {
  padding: 9px 16px;
  border-radius: 12px;
  border: none;
  background: linear-gradient(135deg, #9147ff, #3b82f6);
  color: #fff;
  font-size: 12px;
  cursor: pointer;
  font-weight: 600;
  transition: opacity 0.15s, transform 0.15s;
  align-self: stretch;
  letter-spacing: 0.01em;
}
.confirm-btn:disabled { opacity: 0.35; cursor: default; }
.confirm-btn:not(:disabled):hover { opacity: 0.9; transform: translateY(-1px); }
.confirm-btn:not(:disabled):active { transform: scale(0.97); }

/* ── URL panel ── */
.url-row {
  display: flex;
  gap: 8px;
  align-items: stretch;
}
.url-input {
  flex: 1;
  border: 1.5px solid #eee;
  border-radius: 12px;
  padding: 9px 12px;
  font-size: 11px;
  color: #444;
  outline: none;
  min-width: 0;
  transition: border-color 0.2s;
  background: #fafafa;
  box-sizing: border-box;
}
.url-input:focus { border-color: #9147ff; background: #fff; }
.url-input::placeholder { color: #ccc; font-size: 10px; }
.url-go {
  padding: 9px 14px;
  border-radius: 12px;
  flex-shrink: 0;
  align-self: stretch;
}

.url-shortcuts { margin-top: 14px; }
.url-shortcuts-label {
  font-size: 10px;
  color: #bbb;
  margin: 0 0 6px;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  font-weight: 600;
}
.url-chip {
  display: inline-flex;
  align-items: center;
  margin-right: 6px;
  margin-bottom: 4px;
  padding: 4px 10px;
  border: 1.5px solid #eee;
  border-radius: 20px;
  font-size: 10px;
  font-weight: 500;
  color: #666;
  background: #fafafa;
  cursor: pointer;
  transition: all 0.15s;
}
.url-chip:hover { border-color: #9147ff; color: #7c3aed; background: #f5f0ff; }

/* ── Attachment pills ── */
.attachment-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  padding: 6px 10px 0;
}
.attachment-pill {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 3px 8px 3px 10px;
  background: linear-gradient(135deg, rgba(145,71,255,0.1), rgba(59,130,246,0.1));
  border: 1px solid rgba(145,71,255,0.2);
  border-radius: 20px;
  font-size: 10px;
  font-weight: 500;
  color: #6b21e8;
  max-width: 160px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.attachment-pill button {
  background: none;
  border: none;
  cursor: pointer;
  color: #9147ff;
  font-size: 9px;
  padding: 0;
  line-height: 1;
  opacity: 0.5;
  flex-shrink: 0;
  transition: opacity 0.15s;
}
.attachment-pill button:hover { opacity: 1; }

/* ══════════════════════════════════════════
   SUBTITLE BAR — movie-style, always present below card
   ══════════════════════════════════════════ */
.subtitle-bar {
  position: fixed;
  bottom: 52px;
  left: 50%;
  transform: translateX(-50%);
  width: min(620px, 88vw);
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 52px;
  pointer-events: none;
  z-index: 100;
}

.subtitle-text {
  font-family: sans-serif;
  font-size: 16px;
  line-height: 1.6;
  text-align: center;
  border-radius: 14px;
  padding: 10px 22px;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  max-width: 100%;
  word-break: break-word;
  animation: subtitleIn 0.2s ease;
}

@keyframes subtitleIn {
  from { opacity: 0; transform: translateY(4px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* live transcript — dark pill, movie subtitle style */
.subtitle-text.hearing {
  background: rgba(10, 10, 10, 0.75);
  color: #fff;
  font-weight: 400;
  letter-spacing: 0.015em;
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  border: 1px solid rgba(255,255,255,0.07);
}

/* AI response — light card */
.subtitle-text.response {
  background: rgba(255, 255, 255, 0.97);
  color: #1a1a1a;
  font-weight: 500;
  box-shadow: 0 6px 28px rgba(0,0,60,0.13);
}

/* thinking dots */
.subtitle-text.processing {
  background: rgba(145, 71, 255, 0.09);
  border: 1px solid rgba(145,71,255,0.18);
  gap: 8px;
  padding: 14px 26px;
}

/* pulsing purple dot shown while hearing */
.hearing-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #9147ff;
  flex-shrink: 0;
  animation: hearingDot 0.85s ease-in-out infinite;
}

@keyframes hearingDot {
  0%, 100% { opacity: 1;   transform: scale(1);    }
  50%       { opacity: 0.3; transform: scale(0.5);  }
}

/* ══════════════════════════════════════════
   VOICE WAVEFORM — height driven by real mic volume via JS
   ══════════════════════════════════════════ */

.voice-wave {
  display: flex;
  align-items: flex-end;
  gap: 4px;
  height: 36px;
  margin-top: 10px;
}

.wave-bar {
  width: 4px;
  height: 4px;
  background: linear-gradient(to top, #9147ff, #3b82f6);
  border-radius: 3px;
  transition: height 0.07s ease-out;
  opacity: 0.75;
}

/* ══════════════════════════════════════════
   MIC STATUS PILL
   ══════════════════════════════════════════ */

.mic-status {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  background: rgba(255,255,255,0.85);
  border-radius: 999px;
  box-shadow: 0 2px 12px rgba(0,0,60,0.08);
  font-family: sans-serif;
  font-size: 11px;
  font-weight: 500;
  color: #bbb;
  transition: all 0.3s ease;
  backdrop-filter: blur(8px);
}

.mic-status.listening {
  color: #9147ff;
}

.mic-status.speaking {
  color: #3b82f6;
  box-shadow: 0 2px 16px rgba(59,130,246,0.2);
}

.mic-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #dedfe0;
  transition: background 0.3s ease;
}

.mic-status.listening .mic-dot {
  background: #9147ff;
  animation: micPulse 2s ease-in-out infinite;
}

.mic-status.speaking .mic-dot {
  background: #3b82f6;
  animation: micPulse 0.6s ease-in-out infinite;
}

@keyframes micPulse {
  0%, 100% { transform: scale(1); opacity: 1; }
  50%       { transform: scale(1.4); opacity: 0.7; }
}

/* ══════════════════════════════════════════
   LISTENING STATE — eyes go wide + glow
   ══════════════════════════════════════════ */
.eyes.listening-eyes .eye {
  animation: none !important;
  height: 52px !important;
  background-color: #fff;
  box-shadow:
    0 0 12px rgba(255, 255, 255, 0.9),
    0 0 24px rgba(145, 71, 255, 0.5),
    0 0 40px rgba(59, 130, 246, 0.3);
  animation: listeningPulse 0.8s ease-in-out infinite !important;
}

@keyframes listeningPulse {
  0%, 100% {
    box-shadow:
      0 0 8px rgba(255,255,255,0.8),
      0 0 18px rgba(145,71,255,0.4),
      0 0 32px rgba(59,130,246,0.2);
    transform: scaleY(1);
  }
  50% {
    box-shadow:
      0 0 14px rgba(255,255,255,1),
      0 0 28px rgba(145,71,255,0.7),
      0 0 50px rgba(59,130,246,0.4);
    transform: scaleY(1.08);
  }
}

/* ── Processing dots in subtitle ── */
.subtitle-text.processing {
  background: rgba(145, 71, 255, 0.08);
  gap: 6px;
  padding: 12px 20px;
}
.proc-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: linear-gradient(135deg, #9147ff, #3b82f6);
  animation: procBounce 1.1s ease-in-out infinite;
  display: inline-block;
}
.proc-dot:nth-child(1) { animation-delay: 0s; }
.proc-dot:nth-child(2) { animation-delay: 0.18s; }
.proc-dot:nth-child(3) { animation-delay: 0.36s; }
@keyframes procBounce {
  0%, 100% { transform: translateY(0);    opacity: 0.4; }
  50%       { transform: translateY(-6px); opacity: 1;   }
}
`;

/* ── sub-components (pure, no closures over pipeline) ── */
function ThinkingFace() {
  return (
    <>
      <div className="thought-bubble">
        <div className="thought-cloud">
          <span className="cloud-dot" /><span className="cloud-dot" /><span className="cloud-dot" />
        </div>
        <span className="thought-dot td3" />
        <span className="thought-dot td2" />
        <span className="thought-dot td1" />
      </div>
      <div className="thinking-face">
        <div className="thinking-eyes">
          <span className="thinking-eye eye-left" />
          <span className="thinking-eye eye-right" />
        </div>
      </div>
    </>
  );
}

function VoiceWave({ volume }) {
  const mults = [0.5, 0.85, 1.0, 0.85, 0.5];
  return (
    <div className="voice-wave">
      {mults.map((m, i) => (
        <span key={i} className="wave-bar" style={{ height: `${4 + volume * 28 * m}px` }} />
      ))}
    </div>
  );
}

/* ══════════════════════════════════════════
   MAIN
   ══════════════════════════════════════════ */
export default function AiCard({ 
  mode = 'idle', 
  isSpeaking = false,
  isListening = false,
  transcript = '',
  response = '',
  volume = 0,
  eyePos = { x: 0, y: 0 }
}) {
  const sleeping = mode === 'sleeping';
  const thinking = mode === 'thinking';
  const speaking = mode === 'speaking';
  const booting = mode === 'booting';
  const isError = mode === 'error';

  const eyeStyle = {
    transform: `translateX(calc(-50% + ${eyePos.x}px)) translateY(${eyePos.y}px)`,
    transition: 'transform 0.7s cubic-bezier(0.34,1.56,0.64,1)',
  };

  const subtitleContent = () => {
    if (booting) return <span className="subtitle-text processing"><span className="proc-dot"/><span className="proc-dot"/><span className="proc-dot"/></span>;
    if (isError) return <span className="subtitle-text response">🎤 Please allow microphone access and reload</span>;
    if (thinking) return <span className="subtitle-text processing"><span className="proc-dot"/><span className="proc-dot"/><span className="proc-dot"/></span>;
    if (transcript) return <span className="subtitle-text hearing" key={transcript}><span className="hearing-dot"/>{transcript}</span>;
    if (response) return <span className="subtitle-text response">{response}</span>;
    return null;
  };

  return (
    <>
      <style>{cssStyles}</style>
      <div className="container-ai-voice">

        <div className={`card${sleeping ? ' sleeping' : ''}${thinking ? ' thinking' : ''}`}>
          <div className="background-blur-balls">
            <div className="balls">
              <span className="ball rosa" /><span className="ball violet" />
              <span className="ball green" /><span className="ball cyan" />
            </div>
          </div>

          <div className="content-card">
            <div className="background-blur-card">

              <div
                className={`eyes${sleeping || thinking ? ' hidden' : ''}${isListening ? ' listening-eyes' : ''}`}
                style={eyeStyle}
              >
                <span className="eye" /><span className="eye" />
              </div>

              {sleeping && !thinking && (
                <div className="eyes sleeping-eyes">
                  <span className="eye-closed" /><span className="eye-closed" />
                  <div className="zzz-container">
                    <span className="zzz z1">Z</span>
                    <span className="zzz z2">z</span>
                    <span className="zzz z3">z</span>
                  </div>
                </div>
              )}

              {thinking && <ThinkingFace />}

            </div>
          </div>

          {!sleeping && !thinking && <VoiceWave volume={speaking ? volume : 0} />}
        </div>

        {/* subtitle — fixed to bottom of screen, always mounted */}
        <div className="subtitle-bar">
          {subtitleContent()}
        </div>

        {/* status pill */}
        {!sleeping && !booting && !isError && (
          <div className={`mic-status${speaking || thinking ? ' speaking' : ' listening'}`}>
            <span className="mic-dot" />
            <span className="mic-label">
              {speaking ? 'Hearing you…' : thinking ? 'Thinking…' : 'Listening'}
            </span>
          </div>
        )}

      </div>
    </>
  );
}