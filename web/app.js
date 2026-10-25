'use strict';

const form = document.getElementById('search-form');
const questionField = document.getElementById('question');
const searchButton = document.getElementById('search-button');
const results = document.getElementById('results');
const errorBox = document.getElementById('request-error');
let source = null;
let inFlight = false;

function node(tag, className, text) {
  const element = document.createElement(tag);
  if (className) element.className = className;
  if (text !== undefined) element.textContent = text;
  return element;
}

function safeSourceLink(url, excerpt) {
  const fallback = 'https://www.nhsa.gov.cn/art/2025/3/16/art_14_16010.html';
  try {
    const parsed = new URL(url);
    if (parsed.protocol !== 'https:' || parsed.hostname !== 'www.nhsa.gov.cn') return fallback;
    parsed.hash = excerpt ? 'zoom:~:text=' + encodeURIComponent(excerpt.slice(0, 35)).replace(/-/g, '%2D') : '';
    return parsed.href;
  } catch {
    return fallback;
  }
}

function clearError() {
  errorBox.hidden = true;
  errorBox.textContent = '';
}

function showError(message) {
  errorBox.textContent = message;
  errorBox.hidden = false;
}

function displayDate(value) {
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value || 'Unavailable' : date.toLocaleString('en-GB', { hour12: false });
}

async function loadSource() {
  try {
    const response = await fetch('/api/source', { cache: 'no-store' });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'The verified source is unavailable.');
    source = data.source;
    document.getElementById('source-heading').textContent = source.title;
    document.getElementById('source-publisher').textContent = source.publisher;
    document.getElementById('source-published').textContent = source.published_date;
    document.getElementById('source-retrieved').textContent = displayDate(source.retrieved_at);
    document.getElementById('source-cache').textContent = source.cache_state + ' · ' + source.snapshot_sha256.slice(0, 10);
    document.getElementById('source-link').href = safeSourceLink(source.url);
    document.getElementById('source-status').textContent = 'Source identity and snapshot verified.';
  } catch (error) {
    document.getElementById('source-publisher').textContent = 'Source not loaded';
    document.getElementById('source-status').textContent = error.message;
    showError('The source is unavailable. Restart the server with network access or a verified local cache.');
  }
}

function renderResult(data) {
  results.replaceChildren();
  results.append(node('p', 'result-reason', 'Checked question: ' + data.question));
  const insufficient = data.status === 'insufficient';
  const conditional = data.status === 'conditional';
  results.append(node('span', 'result-label' + (insufficient ? ' insufficient' : ''), insufficient ? 'Insufficient evidence' : conditional ? 'Evidence with conditions' : 'Original evidence located'));
  results.append(node('h3', 'result-title', insufficient ? 'This guide cannot establish that.' : conditional ? 'Keep these conditions together.' : 'Check the original wording.'));
  results.append(node('p', 'result-reason', data.reason));
  const recordSource = data.source || source || {};
  const evidence = Array.isArray(data.evidence) ? data.evidence : [];
  for (const passage of evidence) {
    const card = node('article', 'evidence-card' + (insufficient ? ' related' : ''));
    card.append(node('span', 'evidence-kind', insufficient ? 'Related passage · does not prove the claim' : 'Original Chinese passage'));
    const location = node('p', 'evidence-section', passage.section || 'Article body');
    location.lang = 'zh-CN';
    card.append(location);
    const quote = node('blockquote', '', passage.text);
    quote.lang = 'zh-CN';
    card.append(quote);
    if (passage.english_translation) {
      const translation = node('div', 'translation');
      translation.append(node('span', 'evidence-kind', 'AI English translation · not official'));
      translation.append(node('p', '', passage.english_translation));
      translation.append(node('p', 'translation-note', 'English button names are translations. Check the original Chinese wording above.'));
      card.append(translation);
    }
    if (conditional) card.append(node('p', 'condition-note', 'The guide limits this route to some regions and eligible participants who cannot provide recognition materials. An application is not an approval.'));
    card.append(node('p', 'evidence-source', (recordSource.publisher || 'Official guide') + ' · published ' + (recordSource.published_date || 'date unavailable')));
    const link = node('a', '', 'Open original · use the section label if highlighting is unavailable ↗');
    link.href = safeSourceLink(recordSource.url, passage.text);
    link.target = '_blank';
    link.rel = 'noopener noreferrer';
    card.append(link);
    results.append(card);
  }
  results.append(node('p', 'boundary-note', 'Scope: this single guide and a small set of procedural topics. English explanations and marked translations are AI-authored display notes, not official guidance. The Chinese quotation is the original evidence.'));
}

async function submitQuestion() {
  if (inFlight) return;
  clearError();
  const question = questionField.value.trim();
  if (!question) {
    showError('Enter a question first.');
    questionField.focus();
    return;
  }
  if (question.length > 500) {
    showError('Keep the question within 500 characters.');
    return;
  }
  inFlight = true;
  searchButton.disabled = true;
  questionField.readOnly = true;
  document.querySelectorAll('[data-question]').forEach(button => { button.disabled = true; });
  searchButton.textContent = 'Checking the guide…';
  results.setAttribute('aria-busy', 'true');
  results.replaceChildren(node('p', 'result-reason', 'Looking for original evidence…'));
  try {
    const response = await fetch('/api/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'The search could not be completed.');
    renderResult(data);
  } catch (error) {
    results.replaceChildren(node('p', 'result-reason', 'No result has been inferred for this request.'));
    showError(error.message);
  } finally {
    inFlight = false;
    searchButton.disabled = false;
    questionField.readOnly = false;
    document.querySelectorAll('[data-question]').forEach(button => { button.disabled = false; });
    searchButton.textContent = 'Find evidence →';
    results.setAttribute('aria-busy', 'false');
  }
}

form.addEventListener('submit', (event) => {
  event.preventDefault();
  submitQuestion();
});
questionField.addEventListener('keydown', (event) => {
  if (event.key === 'Enter' && !event.shiftKey && !event.isComposing) {
    event.preventDefault();
    submitQuestion();
  }
});
document.querySelectorAll('[data-question]').forEach((button) => {
  button.addEventListener('click', () => {
    if (inFlight) return;
    questionField.value = button.dataset.question;
    questionField.focus();
    submitQuestion();
  });
});
loadSource();
