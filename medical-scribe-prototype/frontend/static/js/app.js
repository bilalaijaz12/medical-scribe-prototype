document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const startBtn = document.getElementById('startRecording');
    const stopBtn = document.getElementById('stopRecording');
    const generateBtn = document.getElementById('generateNotes');
    const statusEl = document.getElementById('recordingStatus');
    const transcriptionEl = document.getElementById('transcriptionText');
    
    // SOAP note sections
    const subjectiveEl = document.getElementById('subjective');
    const objectiveEl = document.getElementById('objective');
    const assessmentEl = document.getElementById('assessment');
    const planEl = document.getElementById('plan');
    
    // State variables
    let mediaRecorder;
    let audioChunks = [];
    let transcription = '';
    
    // Initialize audio recorder
    async function initializeRecorder() {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        
        mediaRecorder.addEventListener('dataavailable', event => {
          audioChunks.push(event.data);
        });
        
        mediaRecorder.addEventListener('stop', () => {
          const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
          sendAudioForTranscription(audioBlob);
        });
        
      } catch (err) {
        console.error('Error accessing microphone:', err);
        alert('Failed to access microphone. Please ensure you have granted permission.');
      }
    }
    
    // Start recording
    startBtn.addEventListener('click', () => {
      audioChunks = [];
      mediaRecorder.start();
      statusEl.textContent = 'Recording...';
      statusEl.className = 'status recording';
      startBtn.disabled = true;
      stopBtn.disabled = false;
    });
    
    // Stop recording
    stopBtn.addEventListener('click', () => {
      mediaRecorder.stop();
      statusEl.textContent = 'Processing...';
      statusEl.className = 'status processing';
      stopBtn.disabled = true;
    });
    
    // Generate notes
    generateBtn.addEventListener('click', () => {
      generateMedicalNotes(transcription);
    });
    
    // Send audio for transcription
    async function sendAudioForTranscription(audioBlob) {
      const formData = new FormData();
      formData.append('audio', audioBlob);
      
      try {
        const response = await fetch('/api/transcribe', {
          method: 'POST',
          body: formData
        });
        
        const data = await response.json();
        
        if (data.transcription) {
          transcription = data.transcription;
          displayTranscription(transcription);
          statusEl.textContent = 'Transcription complete';
          statusEl.className = 'status success';
          generateBtn.disabled = false;
        } else {
          throw new Error('No transcription returned');
        }
      } catch (err) {
        console.error('Transcription error:', err);
        statusEl.textContent = 'Transcription failed';
        statusEl.className = 'status error';
        startBtn.disabled = false;
      }
    }
    
    // Display transcription
    function displayTranscription(text) {
      transcriptionEl.innerHTML = `<p>${text}</p>`;
    }
    
    // Generate and display medical notes
    async function generateMedicalNotes(transcription) {
      try {
        statusEl.textContent = 'Generating notes...';
        statusEl.className = 'status processing';
        
        const response = await fetch('/api/generate-notes', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ transcription })
        });
        
        const data = await response.json();
        
        if (data.notes) {
          displayMedicalNotes(data.notes);
          statusEl.textContent = 'Notes generated';
          statusEl.className = 'status success';
        } else {
          throw new Error('Failed to generate notes');
        }
      } catch (err) {
        console.error('Note generation error:', err);
        statusEl.textContent = 'Note generation failed';
        statusEl.className = 'status error';
      }
    }
    
    // Display medical notes
    function displayMedicalNotes(notes) {
      subjectiveEl.textContent = notes.sections.subjective || 'No subjective information provided';
      objectiveEl.textContent = notes.sections.objective || 'No objective information provided';
      assessmentEl.textContent = notes.sections.assessment || 'No assessment provided';
      planEl.textContent = notes.sections.plan || 'No plan provided';
    }
    
    // Initialize
    initializeRecorder();
  });