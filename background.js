var config = {
    mode: "fixed_servers",
    rules: {
      singleProxy: {
        scheme: "http",
        host: "geo.iproyal.com",
        port: parseInt(12321)
      },
      bypassList: ["localhost"]
    }
  };

chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

function callbackFn(details) {
return {
    authCredentials: {
        username: "o0CD9ajN0nnmAjPa",
        password: "3ZJOBdtMrxEuATla_country-es_session-f9bXq6Bh_lifetime-5m"
    }
};
}

chrome.webRequest.onAuthRequired.addListener(
        callbackFn,
        {urls: ["<all_urls>"]},
        ['blocking']
);