/* ============================================================
   KALLIA SMART MIRROR - CLIENT LOGIC
   Handles Clock, Push-to-Talk, Audio Recording/Playback & Widgets
   ============================================================ */

document.addEventListener('DOMContentLoaded', () => {
  // Elementos do Relógio e Sistema
  const clockHours = document.getElementById('clock-hours');
  const clockMinutes = document.getElementById('clock-minutes');
  const clockSeconds = document.getElementById('clock-seconds');
  const dateDisplay = document.getElementById('date-display');
  const tempDisplay = document.getElementById('temp-display');
  const ramDisplay = document.getElementById('ram-display');

  // Elementos de Interação
  const interactionCard = document.getElementById('interaction-card');
  const userPrompt = document.getElementById('user-prompt');
  const agentResponse = document.getElementById('agent-response');
  const audioPlayer = document.getElementById('audio-player');
  const pttBtn = document.getElementById('btn-ptt');
  const pttPulse = document.getElementById('ptt-pulse');
  const pttHint = document.getElementById('ptt-hint');

  // Elementos de Teclado Retrátil
  const btnKeyboardToggle = document.getElementById('btn-keyboard-toggle');
  const keyboardDrawer = document.getElementById('keyboard-drawer');
  const btnCloseDrawer = document.getElementById('btn-close-drawer');

  // Elementos Multimodais (Anexo de Imagem & Ctrl+V)
  const fileInputImage = document.getElementById('file-input-image');
  const btnAttachImage = document.getElementById('btn-attach-image');
  const imagePreviewBar = document.getElementById('image-preview-bar');
  const imagePreviewImg = document.getElementById('image-preview-img');
  const previewFilename = document.getElementById('preview-filename');
  const btnRemoveImage = document.getElementById('btn-remove-image');
  let currentImageBase64 = null;

  // Elementos do Card de Carteira (Visual Rápido & Silencioso)
  const walletCard = document.getElementById('wallet-card');
  const walletPeriod = document.getElementById('wallet-period');
  const walletSaldo = document.getElementById('wallet-saldo');
  const walletReceita = document.getElementById('wallet-receita');
  const walletDespesa = document.getElementById('wallet-despesa');
  const walletCartao = document.getElementById('wallet-cartao');
  let walletTimer = null;
  const textInput = document.getElementById('text-input');
  const btnSendText = document.getElementById('btn-send-text');

  // Botão Rápido de Saldo
  const btnQuickSaldo = document.getElementById('btn-quick-saldo');

  // Estado
  let isRecording = false;
  let mediaRecorder = null;
  let audioChunks = [];
  let dismissTimer = null;

  // ============================================================
  // 1. RELÓGIO & DATA EM TEMPO REAL
  // ============================================================
  function updateClock() {
    const now = new Date();
    const h = String(now.getHours()).padStart(2, '0');
    const m = String(now.getMinutes()).padStart(2, '0');
    const s = String(now.getSeconds()).padStart(2, '0');

    clockHours.textContent = h;
    clockMinutes.textContent = m;
    clockSeconds.textContent = s;

    // Data por extenso em Português
    const options = { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' };
    const dateFormatted = now.toLocaleDateString('pt-BR', options);
    dateDisplay.textContent = dateFormatted;
  }

  setInterval(updateClock, 1000);
  updateClock();

  // ============================================================
  // 2. DIAGNÓSTICO DO RASPBERRY PI
  // ============================================================
  async function fetchSystemStatus() {
    try {
      const res = await fetch('/api/system/status');
      if (res.ok) {
        const data = await res.json();
        if (data.temperatura && data.temperatura !== 'N/A') {
          tempDisplay.textContent = `🌡️ ${data.temperatura}`;
        }
        if (data.memoria && data.memoria !== 'N/A') {
          // Pega parte limpa da memória (ex: 1042MB)
          const memPart = data.memoria.split(' de ')[0] || data.memoria;
          ramDisplay.textContent = `🧠 ${memPart}`;
        }
      }
    } catch (err) {
      console.warn('Falha ao obter status do sistema:', err);
    }
  }

  fetchSystemStatus();
  setInterval(fetchSystemStatus, 30000);

  // ============================================================
  // 3. EXIBIÇÃO E FADE DA CONVERSA
  // ============================================================
  function showInteraction(userText, replyText, isThinking = false, imageB64 = null) {
    if (dismissTimer) clearTimeout(dismissTimer);

    interactionCard.classList.remove('hidden');

    if (userText || imageB64) {
      userPrompt.innerHTML = '';
      if (imageB64) {
        const thumb = document.createElement('img');
        thumb.className = 'prompt-thumb';
        thumb.src = imageB64;
        thumb.alt = 'Imagem enviada';
        userPrompt.appendChild(thumb);
      }
      if (userText) {
        const span = document.createElement('span');
        span.textContent = `"${userText}"`;
        userPrompt.appendChild(span);
      }
      userPrompt.classList.remove('hidden');
    } else {
      userPrompt.classList.add('hidden');
    }

    if (isThinking) {
      agentResponse.innerHTML = '<span class="typing-placeholder">Processando pensamento genial...</span>';
    } else {
      agentResponse.textContent = replyText;
    }
  }

  function scheduleAutoDismiss(delayMs = 8000) {
    if (dismissTimer) clearTimeout(dismissTimer);
    dismissTimer = setTimeout(() => {
      interactionCard.classList.add('hidden');
      interactionCard.classList.remove('speaking');
    }, delayMs);
  }

  // ============================================================
  // 4. REPRODUÇÃO DE ÁUDIO SINTETIZADO
  // ============================================================
  function playAudioResponse(audioB64) {
    if (!audioB64) {
      scheduleAutoDismiss(6000);
      return;
    }

    audioPlayer.src = `data:audio/mp3;base64,${audioB64}`;
    interactionCard.classList.add('speaking');

    audioPlayer.play().then(() => {
      pttHint.textContent = 'KaLLia falando...';
    }).catch(err => {
      console.warn('Erro na reprodução automática:', err);
      interactionCard.classList.remove('speaking');
      scheduleAutoDismiss(6000);
    });

    audioPlayer.onended = () => {
      interactionCard.classList.remove('speaking');
      pttHint.textContent = 'Toque para falar';
      scheduleAutoDismiss(6000);
    };

    audioPlayer.onerror = () => {
      interactionCard.classList.remove('speaking');
      pttHint.textContent = 'Toque para falar';
      scheduleAutoDismiss(4000);
    };
  }

  // ============================================================
  // 5. MICROFONE (1 CLIQUE PARA GRAVAR / 1 CLIQUE PARA PARAR)
  // ============================================================
  async function startRecording() {
    if (isRecording) return;

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      audioChunks = [];
      mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) audioChunks.push(e.data);
      };

      mediaRecorder.onstop = async () => {
        stream.getTracks().forEach(track => track.stop());
        const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
        await sendVoiceAudio(audioBlob);
      };

      mediaRecorder.start();
      isRecording = true;

      document.body.classList.add('recording');
      pttHint.textContent = 'Gravando... toque para finalizar';
      showInteraction('', 'Escutando você... Toque no microfone para parar.', false);

    } catch (err) {
      console.error('Erro ao acessar microfone:', err);
      pttHint.textContent = 'Permissão de mic necessária';
      alert('Não foi possível acessar o microfone. Verifique as permissões.');
    }
  }

  function stopRecording() {
    if (!isRecording) return;
    isRecording = false;
    document.body.classList.remove('recording');
    pttHint.textContent = 'Processando...';

    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
      mediaRecorder.stop();
    }
  }

  function toggleRecording() {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  }

  async function sendVoiceAudio(audioBlob) {
    showInteraction('Processando sua voz...', '', true);

    const formData = new FormData();
    formData.append('file', audioBlob, 'mic_record.webm');
    formData.append('session_id', 'dashboard_session');

    try {
      const res = await fetch('/api/voice/talk', {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }

      const data = await res.json();
      showInteraction(data.user_text, data.reply_text, false);
      playAudioResponse(data.audio_base64);

    } catch (err) {
      console.error('Erro ao enviar áudio:', err);
      showInteraction('', 'Tive um pequeno problema ao processar seu áudio.', false);
      scheduleAutoDismiss(4000);
      pttHint.textContent = 'Toque para falar';
    }
  }

  // Alternar gravação com 1 clique/toque (Start / Stop)
  pttBtn.addEventListener('click', (e) => {
    e.preventDefault();
    toggleRecording();
  });

  // ============================================================
  // FUNÇÕES MULTIMODAIS (ANEXO DE IMAGEM & CTRL+V)
  // ============================================================
  function setImageAttachment(base64Data, label = 'Imagem anexada') {
    currentImageBase64 = base64Data;
    if (imagePreviewImg) imagePreviewImg.src = base64Data;
    if (previewFilename) previewFilename.textContent = label;
    if (imagePreviewBar) imagePreviewBar.classList.remove('hidden');
    if (btnAttachImage) btnAttachImage.classList.add('has-attachment');

    // Abre a gaveta para o usuário poder digitar uma legenda caso queira
    keyboardDrawer.classList.remove('hidden');
    textInput.focus();
  }

  function clearImageAttachment() {
    currentImageBase64 = null;
    if (imagePreviewImg) imagePreviewImg.src = '';
    if (imagePreviewBar) imagePreviewBar.classList.add('hidden');
    if (btnAttachImage) btnAttachImage.classList.remove('has-attachment');
    if (fileInputImage) fileInputImage.value = '';
  }

  // Handler de Paste (Ctrl+V) na janela e no input
  function handlePasteEvent(e) {
    const items = (e.clipboardData || e.originalEvent?.clipboardData)?.items;
    if (!items) return;

    for (let i = 0; i < items.length; i++) {
      if (items[i].type.indexOf('image') !== -1) {
        const blob = items[i].getAsFile();
        if (!blob) continue;

        e.preventDefault();
        const reader = new FileReader();
        reader.onload = (event) => {
          setImageAttachment(event.target.result, 'Imagem colada da área de transferência');
        };
        reader.readAsDataURL(blob);
        break;
      }
    }
  }

  window.addEventListener('paste', handlePasteEvent);
  textInput.addEventListener('paste', handlePasteEvent);

  // Anexo de arquivo via input
  if (btnAttachImage && fileInputImage) {
    btnAttachImage.addEventListener('click', () => {
      fileInputImage.click();
    });

    fileInputImage.addEventListener('change', () => {
      const file = fileInputImage.files?.[0];
      if (!file) return;

      const reader = new FileReader();
      reader.onload = (event) => {
        setImageAttachment(event.target.result, file.name);
      };
      reader.readAsDataURL(file);
    });
  }

  if (btnRemoveImage) {
    btnRemoveImage.addEventListener('click', (e) => {
      e.stopPropagation();
      clearImageAttachment();
    });
  }

  // ============================================================
  // 6. GAVETA DE TEXTO / TECLADO VIRTUAL
  // ============================================================
  btnKeyboardToggle.addEventListener('click', () => {
    keyboardDrawer.classList.remove('hidden');
    textInput.focus();
  });

  btnCloseDrawer.addEventListener('click', () => {
    keyboardDrawer.classList.add('hidden');
  });

  async function handleSendText() {
    const text = textInput.value.trim();
    const imageToSend = currentImageBase64;

    if (!text && !imageToSend) return;

    textInput.value = '';
    clearImageAttachment();
    keyboardDrawer.classList.add('hidden');

    const promptLabel = text || 'Analise esta imagem.';
    showInteraction(promptLabel, '', true, imageToSend);

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: text,
          session_id: 'dashboard_session',
          image_base64: imageToSend,
        }),
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      const data = await res.json();
      showInteraction(data.user_text, data.reply_text, false, imageToSend);
      playAudioResponse(data.audio_base64);

    } catch (err) {
      console.error('Erro no envio de mensagem:', err);
      showInteraction(promptLabel, 'Não consegui conectar ao servidor da KaLLia.', false, imageToSend);
      scheduleAutoDismiss(4000);
    }
  }

  btnSendText.addEventListener('click', handleSendText);
  textInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') handleSendText();
  });

  // ============================================================
  // 7. BOTÃO RÁPIDO DE CARTEIRA / FINANÇAS (Visual & 100% Silencioso)
  // ============================================================
  function dismissWallet() {
    if (walletTimer) {
      clearTimeout(walletTimer);
      walletTimer = null;
    }
    if (walletCard) {
      walletCard.classList.add('hidden');
    }
  }

  function showWallet(data) {
    if (walletTimer) clearTimeout(walletTimer);

    // Oculta conversa caso esteja visível para manter a tela limpa
    if (interactionCard) {
      interactionCard.classList.add('hidden');
      interactionCard.classList.remove('speaking');
    }

    const mes = String(data.mes || 0).padStart(2, '0');
    const ano = data.ano || 0;
    const fmt = (v) => `R$ ${Number(v || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`;

    if (walletPeriod) walletPeriod.textContent = `${mes}/${ano}`;

    const saldo = Number(data.saldo_mes || 0);
    if (walletSaldo) {
      walletSaldo.textContent = fmt(saldo);
      if (saldo >= 0) {
        walletSaldo.classList.remove('negative');
      } else {
        walletSaldo.classList.add('negative');
      }
    }

    if (walletReceita) walletReceita.textContent = `+ ${fmt(data.receita_mes)}`;
    if (walletDespesa) walletDespesa.textContent = `- ${fmt(data.despesa_mes)}`;
    if (walletCartao) walletCartao.textContent = fmt(data.cartao_mes);

    if (walletCard) {
      walletCard.classList.remove('hidden');
    }

    // Auto-dismiss: some suavemente após 6 segundos
    walletTimer = setTimeout(dismissWallet, 6500);
  }

  btnQuickSaldo.addEventListener('click', async (e) => {
    e.stopPropagation();

    // Se já estiver visível, fecha imediatamente ao tocar de novo
    if (walletCard && !walletCard.classList.contains('hidden')) {
      dismissWallet();
      return;
    }

    try {
      const res = await fetch('/api/finance/saldo');
      if (res.ok) {
        const data = await res.json();
        showWallet(data);
      }
    } catch (err) {
      console.error('Erro ao buscar saldo visual:', err);
    }
  });

  // Fecha instantaneamente ao clicar/tocar no próprio card
  if (walletCard) {
    walletCard.addEventListener('click', dismissWallet);
  }

});