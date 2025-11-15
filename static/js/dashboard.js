document.addEventListener('DOMContentLoaded', function() {
  const resultJSON = localStorage.getItem('analysis_result');
  
  if (!resultJSON) {
    alert('No analysis data found.');
    window.location.href = '/';
    return;
  }

  const data = JSON.parse(resultJSON);
  console.log('Dashboard Data:', data);

  // ========== SENTIMENT (Circle) ==========
  const sentiment = data.sentiment_analysis || {};
  const sentimentPercent = Math.round((sentiment.confidence || 0) * 100);
  const sentimentLabel = sentiment.sentiment || 'Neutral';
  
  document.getElementById('sentiment-percent').textContent = sentimentPercent + '%';
  document.getElementById('sentiment-label').textContent = sentimentLabel;

  const sentimentCirc = 2 * Math.PI * 60;
  const sentimentDash = (sentimentPercent / 100) * sentimentCirc;
  const sentimentProg = document.getElementById('sentiment-progress');
  sentimentProg.style.strokeDasharray = sentimentDash + ',' + sentimentCirc;

  // ========== AI DETECTION (Gauge) ==========
  const aiPercent = Math.round((data.ai_text_detection?.ai_generated_probability || 0) * 100);
  document.getElementById('ai-percent').textContent = aiPercent + '%';

  const aiCirc = Math.PI * 70; // semicircle
  const aiDash = (aiPercent / 100) * aiCirc;
  const aiGauge = document.getElementById('ai-gauge');
  aiGauge.style.strokeDasharray = aiDash + ',' + aiCirc;

  // ========== EMOTIONS (Bars) ==========
  const emotions = data.emotion_detection || {};
  const emotionChart = document.getElementById('emotion-chart');
  emotionChart.innerHTML = '';

  let delay = 0;
  Object.entries(emotions).forEach(([emotion, value]) => {
    const barItem = document.createElement('div');
    barItem.className = 'emotion-bar-item';

    const label = document.createElement('div');
    label.className = 'emotion-label';
    label.textContent = emotion;

    const barBg = document.createElement('div');
    barBg.className = 'emotion-bar-bg';

    const barFill = document.createElement('div');
    barFill.className = 'emotion-bar-fill';
    barFill.style.transition = `width 1s cubic-bezier(0.34, 1.56, 0.64, 1) ${delay}s`;
    setTimeout(() => {
      barFill.style.width = (value * 100) + '%';
    }, 50);

    const percent = document.createElement('div');
    percent.className = 'emotion-percent';
    percent.textContent = Math.round(value * 100) + '%';

    barBg.appendChild(barFill);
    barItem.appendChild(label);
    barItem.appendChild(barBg);
    barItem.appendChild(percent);
    emotionChart.appendChild(barItem);

    delay += 0.1;
  });

  // ========== COHERENCE ==========
  document.getElementById('coherence-val').textContent = (data.coherence_score || 0).toFixed(2);

  // ========== CATEGORY ==========
  document.getElementById('category-val').textContent = data.category?.[0] || 'Unknown';

  // ========== READABILITY ==========
  const readability = data.readability_analysis || {};
  let readabilityHTML = '<pre>';
  Object.entries(readability).forEach(([key, value]) => {
    readabilityHTML += `${key}: ${typeof value === 'number' ? value.toFixed(2) : value}\n`;
  });
  readabilityHTML += '</pre>';
  document.getElementById('readability-val').innerHTML = readabilityHTML;

  // ========== HASHTAGS ==========
  const hashtags = data.hashtag_suggestions || [];
  const hashtagsContainer = document.getElementById('hashtags-container');
  hashtagsContainer.innerHTML = '';

  hashtags.forEach(tag => {
    const chip = document.createElement('span');
    chip.className = 'hashtag-chip';
    chip.textContent = tag;
    chip.addEventListener('click', () => {
      navigator.clipboard.writeText(tag).then(() => {
        chip.textContent = '✓';
        setTimeout(() => {
          chip.textContent = tag;
        }, 1200);
      });
    });
    hashtagsContainer.appendChild(chip);
  });

  // Copy All
  document.getElementById('copy-all-btn').addEventListener('click', () => {
    const allHashtags = hashtags.join(' ');
    navigator.clipboard.writeText(allHashtags).then(() => {
      const status = document.getElementById('copy-status');
      status.textContent = '✓ Copied!';
      status.classList.add('show');
      setTimeout(() => status.classList.remove('show'), 1500);
    });
  });

  // ========== POST PREVIEW ==========
  // If the uploaded file was an image, you can pass it via localStorage
  const postImageData = localStorage.getItem('post_image_data');
  if (postImageData) {
    document.getElementById('post-preview').src = postImageData;
  }
});
