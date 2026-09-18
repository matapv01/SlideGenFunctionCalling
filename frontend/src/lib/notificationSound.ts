export const NOTIFICATIONS_CHANGED_EVENT = "slidegen:notifications-changed";

type BrowserWindow = Window & {
  webkitAudioContext?: typeof AudioContext;
};

let audioContext: AudioContext | null = null;

export function publishNotificationsEnabled(enabled: boolean) {
  if (typeof window === "undefined") return;
  window.dispatchEvent(new CustomEvent(NOTIFICATIONS_CHANGED_EVENT, { detail: { enabled } }));
}

function getAudioContext() {
  if (typeof window === "undefined") return null;
  if (audioContext && audioContext.state !== "closed") return audioContext;

  const AudioContextConstructor = window.AudioContext || (window as BrowserWindow).webkitAudioContext;
  if (!AudioContextConstructor) return null;
  audioContext = new AudioContextConstructor();
  return audioContext;
}

/** Call from the user's send/generate action so later completion audio is allowed by the browser. */
export function unlockNotificationSound() {
  const context = getAudioContext();
  if (context?.state === "suspended") void context.resume().catch(() => undefined);
}

export function playSlideGenerationCompleteSound() {
  const context = getAudioContext();
  if (!context) return;

  const play = () => {
    const now = context.currentTime;
    const master = context.createGain();
    master.gain.setValueAtTime(0.22, now);
    master.connect(context.destination);

    [
      { frequency: 523.25, delay: 0 },
      { frequency: 659.25, delay: 0.11 },
      { frequency: 783.99, delay: 0.22 },
    ].forEach(({ frequency, delay }) => {
      const start = now + delay;
      const oscillator = context.createOscillator();
      const gain = context.createGain();
      oscillator.type = "sine";
      oscillator.frequency.setValueAtTime(frequency, start);
      gain.gain.setValueAtTime(0.0001, start);
      gain.gain.exponentialRampToValueAtTime(0.16, start + 0.025);
      gain.gain.exponentialRampToValueAtTime(0.0001, start + 0.42);
      oscillator.connect(gain);
      gain.connect(master);
      oscillator.start(start);
      oscillator.stop(start + 0.44);
    });

    window.setTimeout(() => master.disconnect(), 900);
  };

  if (context.state === "suspended") {
    void context.resume().then(play).catch(() => undefined);
  } else {
    play();
  }
}
