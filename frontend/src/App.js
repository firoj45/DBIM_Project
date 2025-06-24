import React, { useState, useEffect } from 'react';
import './App.css';

// Animated three-dot loader for button
function AnimatedDotsLoader({ baseText = "Verifying" }) {
  const [dotCount, setDotCount] = useState(0);
  useEffect(() => {
    const interval = setInterval(() => setDotCount(d => (d + 1) % 4), 400);
    return () => clearInterval(interval);
  }, []);
  return <span style={{ fontSize: '0.98em', letterSpacing: 1 }}>{baseText}{'.'.repeat(dotCount)}</span>;
}


// Guidelines will be fetched from the API

const API_BASE_URL = 'http://localhost:8000'; // Local FastAPI server
const VERIFICATION_STATUS = {
  LOADING: 'Executing...',
  SUCCESS: 'Success',
  ERROR: 'Error'
};

function App() {

  const [testCases, setTestCases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Fetch guidelines from the API
  useEffect(() => {
    const fetchGuidelines = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/guidelines`);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        // Only set testCases if the response is an array (guidelines list)
        if (Array.isArray(data)) {
          setTestCases(data);
          setError(null);
        } else {
          console.warn('Guidelines API did not return an array:', data);
          setError('Guidelines data is invalid. Please contact support.');
        }
      } catch (err) {
        console.error('Error fetching guidelines:', err);
        setError('Failed to load guidelines. Please try again later.');
        // Fallback to empty array if API fails
        setTestCases([]);
      } finally {
        setLoading(false);
      }
    };

    fetchGuidelines();
  }, []);
  const [status, setStatus] = useState({});
  const [verificationResults, setVerificationResults] = useState({});
  const [expandedResults, setExpandedResults] = useState({});
  
  // State for test case 4 (Footer Color)
  const [screenshot, setScreenshot] = useState(null);
  const [screenshotName, setScreenshotName] = useState('');
  
  // State for test case 9 (Text Color)
  const [screenshot9, setScreenshot9] = useState(null);
  const [screenshotName9, setScreenshotName9] = useState('');
  
  // State for test case 10 (Logo Lockups)
  const [screenshot10, setScreenshot10] = useState(null);
  const [screenshotName10, setScreenshotName10] = useState('');
  
  // State for test case 11 (Primary Backgrounds)
  const [url11, setUrl11] = useState('');
  
  // State for test case 12 (State Emblem Usage)
  const [screenshot12, setScreenshot12] = useState(null);
  const [screenshotName12, setScreenshotName12] = useState('');
  
  // State for test case 20 (Typography - Noto Sans)
  const [url20, setUrl20] = useState('');
  // States for guidelines 32-38 (Image related test cases)
  const [url32, setUrl32] = useState('');
  const [url33, setUrl33] = useState('');
  const [url34, setUrl34] = useState('');
  const [url35, setUrl35] = useState('');
  const [url36, setUrl36] = useState('');
  const [url37, setUrl37] = useState('');
  const [url38, setUrl38] = useState('');
  // States for guidelines 54-65
  const [url54, setUrl54] = useState('');
  const [url55, setUrl55] = useState('');
  const [url56, setUrl56] = useState('');
  const [url57, setUrl57] = useState('');
  const [url58, setUrl58] = useState('');
  const [url59, setUrl59] = useState('');
  const [url60, setUrl60] = useState('');
  const [url61, setUrl61] = useState('');
  const [url62, setUrl62] = useState('');
  const [url63, setUrl63] = useState('');
  const [url64, setUrl64] = useState('');
  const [url65, setUrl65] = useState('');

  // API endpoint mapping for each test case
  const apiEndpoints = {
    1: '/api/verify/color-palette-selection',
    2: '/api/verify/government-entity-color',
    3: '/api/verify/iconography-color',
    4: '/api/verify/footer-color',
    5: '/api/verify/cta-buttons',
    6: '/api/verify/highlight-backgrounds',
    7: '/api/verify/brand-color-consideration',
    8: '/api/verify/digital-use-only',
    9: '/api/verify/text-color',
    10: '/api/verify/logo-lockups',
    11: '/api/verify/primary-backgrounds',
    12: '/api/verify/state-emblem-usage',
    20: '/api/verify/noto-sans',
    32: '/api/verify/background-image-size',
    33: '/api/verify/banner-image-size',
    34: '/api/verify/thumbnail-image-size',
    35: '/api/verify/image-format',
    36: '/api/verify/high-res-image',
    37: '/api/verify/alt-text',
    38: '/api/verify/alt-text-length',
    54: '/api/verify/server-response-time',
    55: '/api/verify/browser-caching',
    56: '/api/verify/image-optimization',
    57: '/api/verify/js-optimization',
    58: '/api/verify/browser-preloading',
    59: '/api/verify/lazy-loading',
    60: '/api/verify/resource-order',
    61: '/api/verify/critical-resources',
    62: '/api/verify/async-scripts',
    63: '/api/verify/responsiveness',
    64: '/api/verify/cdn',
    65: '/api/verify/cache-headers',
  };



  const toggleResult = (testCaseId) => {
    setExpandedResults(prev => ({
      ...prev,
      [testCaseId]: !prev[testCaseId]
    }));
  };

  // Handle screenshot change for test case 4 (Footer Color)
  const handleScreenshotChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setScreenshot(file);
      setScreenshotName(file.name);
    }
  };

  // Handle screenshot change for test case 9 (Text Color)
  const handleScreenshotChange9 = (e) => {
    const file = e.target.files[0];
    if (file) {
      setScreenshot9(file);
      setScreenshotName9(file.name);
    }
  };

  // Handle screenshot change for test case 10 (Logo Lockups)
  const handleScreenshotChange10 = (e) => {
    const file = e.target.files[0];
    if (file) {
      setScreenshot10(file);
      setScreenshotName10(file.name);
    }
  };

  // Handle screenshot change for test case 12 (State Emblem Usage)
  const handleScreenshotChange12 = (e) => {
    const file = e.target.files[0];
    if (file) {
      setScreenshot12(file);
      setScreenshotName12(file.name);
    }
  };

  const handleExecute = async (testCaseId) => {
    if (testCaseId === 4) {
      await handleFooterColorVerify();
      return;
    }
    if (testCaseId === 9) {
      await handleTextColorVerify();
      return;
    }
    if (testCaseId === 10) {
      await handleLogoLockupVerify();
      return;
    }
    if (testCaseId === 11) {
      await handlePrimaryBackgroundsVerify();
      return;
    }
    if (testCaseId === 12) {
      await handleStateEmblemUsageVerify();
      return;
    }
    if (testCaseId === 20) {
      if (!url20) {
        alert('Please enter a website URL');
        return;
      }
      await handleNotoSansVerify();
      return;
    }
    // Guidelines 32-38 and 54-65
    if ((testCaseId >= 32 && testCaseId <= 38) || (testCaseId >= 54 && testCaseId <= 65)) {
      // Use the corresponding url state
      const urlStates = {
        32: url32, 33: url33, 34: url34, 35: url35, 36: url36, 37: url37, 38: url38,
        54: url54, 55: url55, 56: url56, 57: url57, 58: url58, 59: url59,
        60: url60, 61: url61, 62: url62, 63: url63, 64: url64, 65: url65
      };
      const urlVal = urlStates[testCaseId];
      if (!urlVal) {
        alert('Please enter a website URL');
        return;
      }
      setStatus(prev => ({ ...prev, [testCaseId]: VERIFICATION_STATUS.LOADING }));
      setExpandedResults(prev => ({ ...prev, [testCaseId]: true }));
      try {
        let endpoint = apiEndpoints[testCaseId];
        if (!endpoint) throw new Error(`No endpoint found for test case ${testCaseId}`);
        let fetchUrl = `${API_BASE_URL}${endpoint}`;
        const separator = endpoint.includes('?') ? '&' : '?';
        fetchUrl = `${fetchUrl}${separator}url=${encodeURIComponent(urlVal)}`;
        const response = await fetch(fetchUrl);
        if (!response.ok) {
          const errorText = await response.text();
          throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
        }
        const result = await response.json();
        setVerificationResults(prev => ({ ...prev, [testCaseId]: result }));
        setStatus(prev => ({ ...prev, [testCaseId]: result.success ? VERIFICATION_STATUS.SUCCESS : VERIFICATION_STATUS.ERROR }));
      } catch (error) {
        setStatus(prev => ({ ...prev, [testCaseId]: VERIFICATION_STATUS.ERROR }));
        setVerificationResults(prev => ({
          ...prev,
          [testCaseId]: {
            success: false,
            message: `Error: ${error.message}`,
            timestamp: new Date().toISOString(),
            details: { error: error.toString() }
          }
        }));
      }
      return;
    }
    setStatus(prev => ({
      ...prev,
      [testCaseId]: VERIFICATION_STATUS.LOADING
    }));

    // Auto-expand the result when executing
    setExpandedResults(prev => ({
      ...prev,
      [testCaseId]: true
    }));

    try {
      let endpoint = apiEndpoints[testCaseId];
      if (!endpoint) {
        throw new Error(`No endpoint found for test case ${testCaseId}`);
      }

      // For endpoints that need URL parameter (CTA buttons, Noto Sans verification, etc.)
      let fetchUrl = `${API_BASE_URL}${endpoint}`;
      if ([5, 20].includes(testCaseId)) { // CTA buttons and Noto Sans verification
        const separator = endpoint.includes('?') ? '&' : '?';
        const urlToUse = testCaseId === 20 ? url20 : url11;
        fetchUrl = `${fetchUrl}${separator}url=${encodeURIComponent(urlToUse)}`;
      }

      const response = await fetch(fetchUrl);
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
      }

      const result = await response.json();

      // Update verification results
      setVerificationResults(prev => ({
        ...prev,
        [testCaseId]: result
      }));

      // Update status
      setStatus(prev => ({
        ...prev,
        [testCaseId]: result.success ? VERIFICATION_STATUS.SUCCESS : VERIFICATION_STATUS.ERROR
      }));



    } catch (error) {
      console.error('Error verifying guideline:', error);
      setStatus(prev => ({
        ...prev,
        [testCaseId]: VERIFICATION_STATUS.ERROR
      }));



      // Store error in results
      setVerificationResults(prev => ({
        ...prev,
        [testCaseId]: {
          success: false,
          message: `Error: ${error.message}`,
          timestamp: new Date().toISOString(),
          details: { error: error.toString() }
        }
      }));
    }
  };

  const handleFooterColorVerify = async () => {
    if (!screenshot) return;
    try {
      const formData = new FormData();
      formData.append('file', screenshot);
      const response = await fetch(`${API_BASE_URL}/api/verify/footer-color`, {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();
      setVerificationResults((prev) => ({
        ...prev,
        4: data,
      }));
      setStatus((prev) => ({
        ...prev,
        4: response.ok ? VERIFICATION_STATUS.SUCCESS : VERIFICATION_STATUS.ERROR,
      }));
    } catch (error) {
      setVerificationResults((prev) => ({
        ...prev,
        4: { error: error.message },
      }));
      setStatus((prev) => ({
        ...prev,
        4: VERIFICATION_STATUS.ERROR,
      }));
    }
  };

  const handleTextColorVerify = async () => {
    if (!screenshot9) return;
    try {
      const formData = new FormData();
      formData.append('file', screenshot9);
      const response = await fetch(`${API_BASE_URL}/api/verify/text-color`, {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();
      setVerificationResults((prev) => ({
        ...prev,
        9: data,
      }));
      setStatus((prev) => ({
        ...prev,
        9: response.ok ? VERIFICATION_STATUS.SUCCESS : VERIFICATION_STATUS.ERROR,
      }));
    } catch (error) {
      setVerificationResults((prev) => ({
        ...prev,
        9: { error: error.message },
      }));
      setStatus((prev) => ({
        ...prev,
        9: VERIFICATION_STATUS.ERROR,
      }));
    }
  };

  const handleLogoLockupVerify = async () => {
    if (!screenshot10) {
      setScreenshot10(null);
      setScreenshotName10('');
      return;
    }

    try {
      const formData = new FormData();
      formData.append('file', screenshot10);
      const response = await fetch(`${API_BASE_URL}/api/verify/logo-lockups`, {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();
      setVerificationResults((prev) => ({
        ...prev,
        10: data,
      }));
      setStatus((prev) => ({
        ...prev,
        10: response.ok ? VERIFICATION_STATUS.SUCCESS : VERIFICATION_STATUS.ERROR,
      }));
    } catch (error) {
      setVerificationResults((prev) => ({
        ...prev,
        10: { error: error.message },
      }));
      setStatus((prev) => ({
        ...prev,
        10: VERIFICATION_STATUS.ERROR,
      }));
    }
  };

  const handlePrimaryBackgroundsVerify = async () => {
    if (!url11) {
      alert('Please enter a URL');
      return;
    }
    setStatus(prev => ({
      ...prev,
      11: VERIFICATION_STATUS.LOADING
    }));
    try {
      const endpoint = `${API_BASE_URL}/api/verify/primary-backgrounds?url=${encodeURIComponent(url11)}`;
      const response = await fetch(endpoint);
      const data = await response.json();
      setVerificationResults((prev) => ({
        ...prev,
        11: data,
      }));
      setStatus((prev) => ({
        ...prev,
        11: response.ok ? VERIFICATION_STATUS.SUCCESS : VERIFICATION_STATUS.ERROR,
      }));
    } catch (error) {
      setVerificationResults((prev) => ({
        ...prev,
        11: { error: error.message },
      }));
      setStatus((prev) => ({
        ...prev,
        11: VERIFICATION_STATUS.ERROR,
      }));
    }
  };

  const handleNotoSansVerify = async () => {
    if (!url20) return;
    setStatus(prev => ({
      ...prev,
      20: VERIFICATION_STATUS.LOADING
    }));
    try {
      const endpoint = `${API_BASE_URL}/api/verify/noto-sans?url=${encodeURIComponent(url20)}`;
      const response = await fetch(endpoint);
      const data = await response.json();
      setVerificationResults((prev) => ({
        ...prev,
        20: data,
      }));
      setStatus((prev) => ({
        ...prev,
        20: response.ok ? VERIFICATION_STATUS.SUCCESS : VERIFICATION_STATUS.ERROR,
      }));
    } catch (error) {
      setVerificationResults((prev) => ({
        ...prev,
        20: { error: error.message },
      }));
      setStatus((prev) => ({
        ...prev,
        20: VERIFICATION_STATUS.ERROR,
      }));
    }
  };

  const handleStateEmblemUsageVerify = async () => {
    if (!screenshot12) {
      setScreenshot12(null);
      setScreenshotName12('');
      return;
    }

    try {
      const formData = new FormData();
      formData.append('file', screenshot12);
      const response = await fetch(`${API_BASE_URL}/api/verify/state-emblem-usage`, {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();
      setVerificationResults((prev) => ({
        ...prev,
        12: data,
      }));
      setStatus((prev) => ({
        ...prev,
        12: response.ok ? VERIFICATION_STATUS.SUCCESS : VERIFICATION_STATUS.ERROR,
      }));
    } catch (error) {
      setVerificationResults((prev) => ({
        ...prev,
        12: { error: error.message },
      }));
      setStatus((prev) => ({
        ...prev,
        12: VERIFICATION_STATUS.ERROR,
      }));
    }
  };


  // Helper function to render status badge
  const renderStatusBadge = (testCaseId) => {
    if (testCaseId === 4 && verificationResults[4]) {
      if (verificationResults[4].success === true) {
        return <span className="status-badge success">✅ Verified</span>;
      } else if (verificationResults[4].success === false) {
        return <span className="status-badge error">❌ Not Verified</span>;
      }
    }
    if (testCaseId === 9 && verificationResults[9]) {
      if (verificationResults[9].success === true) {
        return <span className="status-badge success">✅ Verified</span>;
      } else if (verificationResults[9].success === false) {
        return <span className="status-badge error">❌ Not Verified</span>;
      }
    }
    if (testCaseId === 10 && verificationResults[10]) {
      if (verificationResults[10].success === true) {
        return <span className="status-badge success">✅ Verified</span>;
      } else if (verificationResults[10].success === false) {
        return <span className="status-badge error">❌ Not Verified</span>;
      }
    }
    if (testCaseId === 11) {
      if (status[11] === VERIFICATION_STATUS.LOADING) {
        return <span className="status-badge loading">Verifying...</span>;
      }
      if (verificationResults[11]) {
        if (verificationResults[11].success === true) {
          return <span className="status-badge success">✅ Verified</span>;
        } else if (verificationResults[11].success === false) {
          return <span className="status-badge error">❌ Not Verified</span>;
        }
      }
    }
    if (testCaseId === 12 && verificationResults[12]) {
      if (verificationResults[12].success === true) {
        return <span className="status-badge success">✅ Verified</span>;
      } else if (verificationResults[12].success === false) {
        return <span className="status-badge error">❌ Not Verified</span>;
      }
    }
    if (testCaseId === 20 && verificationResults[20]) {
      if (verificationResults[20].success === true) {
        return <span className="status-badge success">✅ Verified</span>;
      } else if (verificationResults[20].success === false) {
        return <span className="status-badge error">❌ Not Verified</span>;
      } else {
        return <span className="status-badge loading">Verification Inconclusive</span>;
      }
    }
    // For guidelines 54-65
    if (testCaseId >= 54 && testCaseId <= 65 && verificationResults[testCaseId]) {
      if (verificationResults[testCaseId].success === true) {
        return <span className="status-badge success">✅ Verified</span>;
      } else if (verificationResults[testCaseId].success === false) {
        return <span className="status-badge error">❌ Not Verified</span>;
      } else {
        return <span className="status-badge loading">Verification Inconclusive</span>;
      }
    }
    const currentStatus = status[testCaseId];
    const result = verificationResults[testCaseId];
    if (currentStatus === VERIFICATION_STATUS.LOADING) {
      return <span className="status-badge loading">Verifying...</span>;
    } else if (currentStatus === VERIFICATION_STATUS.SUCCESS) {
      return <span className="status-badge success">✅ Verified</span>;
    } else if (currentStatus === VERIFICATION_STATUS.ERROR) {
      return <span className="status-badge error">❌ Not Verified</span>;
    } else {
      return null;
    }
  };


  // Helper to format JSON for display
  const formatJson = (obj) => {
    if (!obj) return null;
    return JSON.stringify(obj, null, 2);
  };


  const handleUrlChange11 = (e) => {
    setUrl11(e.target.value);
  };

  const handleUrlChange20 = (e) => {
    setUrl20(e.target.value);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>DBIM Color Guidelines Verification</h1>
        <div className="content">
          {/* <div className="url-verification-section">
              <input
                type="url"
                value={url}
                onChange={handleUrlChange}
                placeholder="Enter URL to verify"
                className="url-input"
              />
            </div> */}

          <h2>Verify Individual Guidelines</h2>

          {loading ? (
            <p>Loading guidelines...</p>
          ) : testCases.length === 0 ? (
            <p>No guidelines found. Please check your connection and try again.</p>
          ) : (
            <div className="test-cases">
              <table>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Guideline</th>
                    <th>Status</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {Array.isArray(testCases) ? testCases.map(testCase => {
                     const result = verificationResults[testCase.id];
                     const isExecuting = status[testCase.id] === VERIFICATION_STATUS.LOADING;
                     const hasResult = !!result;
                     return (
                      <React.Fragment key={testCase.id}>
                        <tr className={`test-case-row ${hasResult ? 'has-result' : ''}`}>
                          <td className="test-case-id">{testCase.id}</td>
                          <td className="test-case-details">
                            <div className="test-case-name">{testCase.name}</div>
                            <div className="test-case-desc">{testCase.description}</div>
                          </td>
                          <td className="test-case-status">
                            {renderStatusBadge(testCase.id)}
                          </td>
                          <td className="test-case-actions">
                            <div className="action-btn-group">
                              <button
                                className={`execute-btn ${isExecuting ? 'executing' : ''}`}
                                onClick={() => {
                                   if (testCase.id === 20) {
                                     handleNotoSansVerify();
                                   } else {
                                     handleExecute(testCase.id);
                                   }
                                }}
                                 disabled={
                                   isExecuting ||
                                   (testCase.id === 4 && !screenshot) ||
                                   (testCase.id === 9 && !screenshot9) ||
                                   (testCase.id === 10 && !screenshot10) ||
                                   (testCase.id === 11 && !url11) ||
                                   (testCase.id === 12 && !screenshot12) ||
                                   (testCase.id === 20 && !url20) ||
                                   (testCase.id === 32 && !url32) ||
                                   (testCase.id === 33 && !url33) ||
                                   (testCase.id === 34 && !url34) ||
                                   (testCase.id === 35 && !url35) ||
                                   (testCase.id === 36 && !url36) ||
                                   (testCase.id === 37 && !url37) ||
                                   (testCase.id === 38 && !url38) ||
                                   (testCase.id === 54 && !url54) ||
                                   (testCase.id === 55 && !url55) ||
                                   (testCase.id === 56 && !url56) ||
                                   (testCase.id === 57 && !url57) ||
                                   (testCase.id === 58 && !url58) ||
                                   (testCase.id === 59 && !url59) ||
                                   (testCase.id === 60 && !url60) ||
                                   (testCase.id === 61 && !url61) ||
                                   (testCase.id === 62 && !url62) ||
                                   (testCase.id === 63 && !url63) ||
                                   (testCase.id === 64 && !url64) ||
                                   (testCase.id === 65 && !url65)
                                 }
                              >
                                {isExecuting ? (
                                  <AnimatedDotsLoader baseText="Verifying" />
                                ) : 'Verify'}
                              </button>
                              {testCase.id === 4 && (
                                <div className="pretty-upload-wrapper">
                                  <input
                                    type="file"
                                    id={`screenshot-upload-${testCase.id}`}
                                    accept="image/*"
                                    className="pretty-upload-input"
                                    onChange={handleScreenshotChange}
                                  />
                                  <label htmlFor={`screenshot-upload-${testCase.id}`} className="pretty-upload-label">
                                    <span className="pretty-upload-btn">📷 Upload Screenshot</span>
                                  </label>
                                  {screenshotName && (
                                    <span className="pretty-upload-filename">{screenshotName}</span>
                                  )}
                                  {screenshot && (
                                    <img
                                      src={URL.createObjectURL(screenshot)}
                                      alt="Screenshot Preview"
                                      className="pretty-upload-preview"
                                    />
                                  )}
                                </div>
                              )}
                              {testCase.id === 9 && (
                                <div className="pretty-upload-wrapper">
                                  <input
                                    type="file"
                                    id={`screenshot-upload-${testCase.id}`}
                                    accept="image/*"
                                    className="pretty-upload-input"
                                    onChange={handleScreenshotChange9}
                                  />
                                  <label htmlFor={`screenshot-upload-${testCase.id}`} className="pretty-upload-label">
                                    <span className="pretty-upload-btn">📷 Upload Screenshot</span>
                                  </label>
                                  {screenshotName9 && (
                                    <span className="pretty-upload-filename">{screenshotName9}</span>
                                  )}
                                  {screenshot9 && (
                                    <img
                                      src={URL.createObjectURL(screenshot9)}
                                      alt="Screenshot Preview"
                                      className="pretty-upload-preview"
                                    />
                                  )}
                                </div>
                              )}
                              {testCase.id === 10 && (
                                <div className="pretty-upload-wrapper">
                                  <input
                                    type="file"
                                    id={`screenshot-upload-${testCase.id}`}
                                    accept="image/*"
                                    className="pretty-upload-input"
                                    onChange={handleScreenshotChange10}
                                  />
                                  <label htmlFor={`screenshot-upload-${testCase.id}`} className="pretty-upload-label">
                                    <span className="pretty-upload-btn">📷 Upload Screenshot</span>
                                  </label>
                                  {screenshot10 && (
                                    <span className="pretty-upload-filename">{screenshot10.name}</span>
                                  )}
                                  {screenshot10 && (
                                    <img
                                      src={URL.createObjectURL(screenshot10)}
                                      alt="Screenshot Preview"
                                      className="pretty-upload-preview"
                                    />
                                  )}
                                </div>
                              )}
                              {(testCase.id === 5 || testCase.id === 20) && (
                                <div className="url-input-wrapper" style={{ width: '100%' }}>
                                  <input
                                    type="url"
                                    id={`url-input-${testCase.id}`}
                                    className="url-input"
                                    value={testCase.id === 20 ? url20 : url11}
                                    onChange={testCase.id === 20 ? handleUrlChange20 : handleUrlChange11}
                                    placeholder={testCase.id === 20 
                                      ? "Enter page URL to verify typography" 
                                      : "Enter website URL"}
                                    style={{ width: '100%', padding: '8px' }}
                                  />
                                </div>
                              )}
                              {((testCase.id >= 32 && testCase.id <= 38) || (testCase.id >= 54 && testCase.id <= 65)) && (
                                <div className="url-input-wrapper" style={{ width: '100%', marginBottom: 8 }}>
                                  <input
                                    type="url"
                                    id={`url-input-${testCase.id}`}
                                    className="url-input"
                                    value={
                                      testCase.id === 32 ? url32 :
                                      testCase.id === 33 ? url33 :
                                      testCase.id === 34 ? url34 :
                                      testCase.id === 35 ? url35 :
                                      testCase.id === 36 ? url36 :
                                      testCase.id === 37 ? url37 :
                                      testCase.id === 38 ? url38 :
                                      testCase.id === 54 ? url54 :
                                      testCase.id === 55 ? url55 :
                                      testCase.id === 56 ? url56 :
                                      testCase.id === 57 ? url57 :
                                      testCase.id === 58 ? url58 :
                                      testCase.id === 59 ? url59 :
                                      testCase.id === 60 ? url60 :
                                      testCase.id === 61 ? url61 :
                                      testCase.id === 62 ? url62 :
                                      testCase.id === 63 ? url63 :
                                      testCase.id === 64 ? url64 :
                                      testCase.id === 65 ? url65 : ''
                                    }
                                    onChange={e => {
                                      const val = e.target.value;
                                      if (testCase.id === 32) setUrl32(val);
                                      else if (testCase.id === 33) setUrl33(val);
                                      else if (testCase.id === 34) setUrl34(val);
                                      else if (testCase.id === 35) setUrl35(val);
                                      else if (testCase.id === 36) setUrl36(val);
                                      else if (testCase.id === 37) setUrl37(val);
                                      else if (testCase.id === 38) setUrl38(val);
                                      else if (testCase.id === 54) setUrl54(val);
                                      else if (testCase.id === 55) setUrl55(val);
                                      else if (testCase.id === 56) setUrl56(val);
                                      else if (testCase.id === 57) setUrl57(val);
                                      else if (testCase.id === 58) setUrl58(val);
                                      else if (testCase.id === 59) setUrl59(val);
                                      else if (testCase.id === 60) setUrl60(val);
                                      else if (testCase.id === 61) setUrl61(val);
                                      else if (testCase.id === 62) setUrl62(val);
                                      else if (testCase.id === 63) setUrl63(val);
                                      else if (testCase.id === 64) setUrl64(val);
                                      else if (testCase.id === 65) setUrl65(val);
                                    }}
                                    placeholder="Enter website URL"
                                    style={{ width: '100%', padding: '8px' }}
                                  />
                                </div>
                              )}
                              {testCase.id === 12 && (
                                <div className="pretty-upload-wrapper">
                                  <input
                                    type="file"
                                    id={`screenshot-upload-${testCase.id}`}
                                    accept="image/*"
                                    className="pretty-upload-input"
                                    onChange={handleScreenshotChange12}
                                  />
                                  <label htmlFor={`screenshot-upload-${testCase.id}`} className="pretty-upload-label">
                                    <span className="pretty-upload-btn">📷 Upload Screenshot</span>
                                  </label>
                                  {screenshotName12 && (
                                    <span className="pretty-upload-filename">{screenshotName12}</span>
                                  )}
                                  {screenshot12 && (
                                    <img
                                      src={URL.createObjectURL(screenshot12)}
                                      alt="Screenshot Preview"
                                      className="pretty-upload-preview"
                                    />
                                  )}
                                </div>
                              )}
                            </div>
                          </td>
                        </tr>
                        {[11, 20].includes(testCase.id)
                          ? ((status[testCase.id] === VERIFICATION_STATUS.LOADING)
                            ? (
                              <tr className="result-row">
                                <td colSpan={4} className="result-details">
                                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                    <span className="loader-spinner" style={{ width: 18, height: 18, border: '3px solid #2196f3', borderTop: '3px solid #fff', borderRadius: '50%', display: 'inline-block', animation: 'spin 1s linear infinite' }}></span>
                                    <span>Verifying...</span>
                                  </div>
                                </td>
                              </tr>
                            )
                            : (hasResult && (
                              <tr className="result-row">
                                <td colSpan={4} className="result-details">
                                  <div className="result-header">
                                    <div className="result-message">
                                      <strong>Result:</strong> {result.message}
                                    </div>
                                    <button
                                      className="toggle-result-btn"
                                      onClick={() => toggleResult(testCase.id)}
                                    >
                                      {expandedResults[testCase.id] ? 'Hide JSON' : 'Show JSON'}
                                    </button>
                                  </div>
                                  {expandedResults[testCase.id] && (
                                    <pre className="result-json">{formatJson(result)}</pre>
                                  )}
                                  <div className="result-timestamp">
                                    {result.timestamp && (
                                      <>Verified at: {new Date(result.timestamp).toLocaleString()}</>
                                    )}
                                  </div>
                                </td>
                              </tr>
                            )))
                          : (hasResult && (
                            <tr className="result-row">
                              <td colSpan={4} className="result-details">
                                <div className="result-header">
                                  <div className="result-message">
                                    <strong>Result:</strong> {result.message}
                                  </div>
                                  <button
                                    className="toggle-result-btn"
                                    onClick={() => toggleResult(testCase.id)}
                                  >
                                    {expandedResults[testCase.id] ? 'Hide JSON' : 'Show JSON'}
                                  </button>
                                </div>
                                {expandedResults[testCase.id] && (
                                  <pre className="result-json">{formatJson(result)}</pre>
                                )}
                                <div className="result-timestamp">
                                  {result.timestamp && (
                                    <>Verified at: {new Date(result.timestamp).toLocaleString()}</>
                                  )}
                                </div>
                              </td>
                            </tr>
                          ))}
                        {testCase.id === 4 && verificationResults[4] && expandedResults[testCase.id] && (
                          <tr className={`result-row expanded`}>
                            <td colSpan="4">
                              <div className="footer-color-result" style={{ textAlign: 'center', margin: '18px 0' }}>
                                {verificationResults[4].details && verificationResults[4].details.hex && (
                                  <>
                                    <div style={{ marginBottom: 8, fontWeight: 600, fontSize: '1.08rem' }}>Detected Color:</div>
                                    <div
                                      style={{
                                        display: 'inline-block',
                                        width: 48,
                                        height: 48,
                                        background: verificationResults[4].details.hex,
                                        border: '2px solid #1a237e',
                                        borderRadius: 8,
                                        marginBottom: 8,
                                        boxShadow: '0 2px 8px rgba(33,150,243,0.13)'
                                      }}
                                    />
                                    <div style={{ fontWeight: 600, marginTop: 6, fontSize: '1.05rem' }}>{verificationResults[4].details.hex}</div>
                                  </>
                                )}
                                {verificationResults[4].error && (
                                  <span style={{ color: 'red' }}>Error: {verificationResults[4].error}</span>
                                )}
                              </div>
                            </td>
                          </tr>
                        )}
                        {testCase.id === 9 && verificationResults[9] && expandedResults[testCase.id] && (
                          <tr className={`result-row expanded`}>
                            <td colSpan="4">
                              <div className="footer-color-result" style={{ textAlign: 'center', margin: '18px 0' }}>
                                {verificationResults[9].details && verificationResults[9].details.hex && (
                                  <>
                                    <div style={{ marginBottom: 8, fontWeight: 600, fontSize: '1.08rem' }}>Detected Color:</div>
                                    <div
                                      style={{
                                        display: 'inline-block',
                                        width: 48,
                                        height: 48,
                                        background: verificationResults[9].details.hex,
                                        border: '2px solid #1a237e',
                                        borderRadius: 8,
                                        marginBottom: 8,
                                        boxShadow: '0 2px 8px rgba(33,150,243,0.13)'
                                      }}
                                    />
                                    <div style={{ fontWeight: 600, marginTop: 6, fontSize: '1.05rem' }}>{verificationResults[9].details.hex}</div>
                                  </>
                                )}
                                {verificationResults[9].error && (
                                  <span style={{ color: 'red' }}>Error: {verificationResults[9].error}</span>
                                )}
                              </div>
                            </td>
                          </tr>
                        )}
                        {testCase.id === 10 && verificationResults[10] && expandedResults[testCase.id] && (
                          <tr className={`result-row expanded`}>
                            <td colSpan="4">
                              <div className="footer-color-result" style={{ textAlign: 'center', margin: '18px 0' }}>
                                {verificationResults[10].details && (
                                  <>
                                    <div style={{ display: 'flex', justifyContent: 'center', gap: 32, marginBottom: 12 }}>
                                      <div>
                                        <div style={{ marginBottom: 4, fontWeight: 600, fontSize: '1.02rem' }}>Background</div>
                                        <div
                                          style={{
                                            display: 'inline-block',
                                            width: 40,
                                            height: 40,
                                            background: verificationResults[10].details.background_hex,
                                            border: '2px solid #1a237e',
                                            borderRadius: 8,
                                            marginBottom: 4,
                                            boxShadow: '0 2px 8px rgba(33,150,243,0.13)'
                                          }}
                                        />
                                        <div style={{ fontWeight: 500, marginTop: 4, fontSize: '0.98rem' }}>{verificationResults[10].details.background_hex}</div>
                                      </div>
                                      <div>
                                        <div style={{ marginBottom: 4, fontWeight: 600, fontSize: '1.02rem' }}>Logo</div>
                                        <div
                                          style={{
                                            display: 'inline-block',
                                            width: 40,
                                            height: 40,
                                            background: verificationResults[10].details.logo_hex,
                                            border: '2px solid #1a237e',
                                            borderRadius: 8,
                                            marginBottom: 4,
                                            boxShadow: '0 2px 8px rgba(33,150,243,0.13)'
                                          }}
                                        />
                                        <div style={{ fontWeight: 500, marginTop: 4, fontSize: '0.98rem' }}>{verificationResults[10].details.logo_hex}</div>
                                      </div>
                                    </div>
                                  </>
                                )}
                                {verificationResults[10].error && (
                                  <span style={{ color: 'red' }}>Error: {verificationResults[10].error}</span>
                                )}
                              </div>
                            </td>
                          </tr>
                        )}
                        {testCase.id === 12 && verificationResults[12] && expandedResults[testCase.id] && (
                          <tr className={`result-row expanded`}>
                            <td colSpan="4">
                              <div className="footer-color-result" style={{ textAlign: 'center', margin: '18px 0' }}>
                                {verificationResults[12].details && (
                                  <>
                                    <div style={{ display: 'flex', justifyContent: 'center', gap: 32, marginBottom: 12 }}>
                                      <div>
                                        <div style={{ marginBottom: 4, fontWeight: 600, fontSize: '1.02rem' }}>Background</div>
                                        <div
                                          style={{
                                            display: 'inline-block',
                                            width: 40,
                                            height: 40,
                                            background: verificationResults[12].details.background_hex,
                                            border: '2px solid #1a237e',
                                            borderRadius: 8,
                                            marginBottom: 4,
                                            boxShadow: '0 2px 8px rgba(33,150,243,0.13)'
                                          }}
                                        />
                                        <div style={{ fontWeight: 500, marginTop: 4, fontSize: '0.98rem' }}>{verificationResults[12].details.background_hex}</div>
                                      </div>
                                      <div>
                                        <div style={{ marginBottom: 4, fontWeight: 600, fontSize: '1.02rem' }}>Emblem</div>
                                        <div
                                          style={{
                                            display: 'inline-block',
                                            width: 40,
                                            height: 40,
                                            background: verificationResults[12].details.emblem_hex,
                                            border: '2px solid #1a237e',
                                            borderRadius: 8,
                                            marginBottom: 4,
                                            boxShadow: '0 2px 8px rgba(33,150,243,0.13)'
                                          }}
                                        />
                                        <div style={{ fontWeight: 500, marginTop: 4, fontSize: '0.98rem' }}>{verificationResults[12].details.emblem_hex}</div>
                                      </div>
                                    </div>
                                  </>
                                )}
                                {verificationResults[12].error && (
                                  <span style={{ color: 'red' }}>Error: {verificationResults[12].error}</span>
                                )}
                              </div>
                            </td>
                          </tr>
                        )}
                      </React.Fragment>
                    );
                  }) : null}
                 </tbody>
              </table>
            </div>
          )}
        </div>
      </header>
    </div>
  );
}

export default App;
