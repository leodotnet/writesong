// 离线状态检测和处理
(function() {
    'use strict';
    
    // 离线状态指示器
    let offlineIndicator = null;
    
    // 创建离线指示器
    function createOfflineIndicator() {
        if (!offlineIndicator) {
            offlineIndicator = document.createElement('div');
            offlineIndicator.className = 'offline-indicator';
            offlineIndicator.innerHTML = '⚠️ 当前处于离线状态，部分功能可能受限';
            document.body.insertBefore(offlineIndicator, document.body.firstChild);
        }
    }
    
    // 显示/隐藏离线指示器
    function toggleOfflineIndicator(show) {
        createOfflineIndicator();
        if (show) {
            offlineIndicator.classList.add('show');
        } else {
            offlineIndicator.classList.remove('show');
        }
    }
    
    // 检测网络状态
    function checkOnlineStatus() {
        if (!navigator.onLine) {
            toggleOfflineIndicator(true);
            console.log('网络连接已断开');
        } else {
            toggleOfflineIndicator(false);
            console.log('网络连接已恢复');
        }
    }
    
    // 监听网络状态变化
    window.addEventListener('online', function() {
        checkOnlineStatus();
        // 网络恢复时尝试重新加载失败的资源
        retryFailedResources();
    });
    
    window.addEventListener('offline', function() {
        checkOnlineStatus();
    });
    
    // 资源加载失败处理
    const failedResources = new Set();
    
    function handleResourceError(event) {
        const resource = event.target;
        const resourceUrl = resource.src || resource.href;
        
        if (resourceUrl && !resourceUrl.startsWith(window.location.origin)) {
            failedResources.add(resourceUrl);
            console.warn('外部资源加载失败:', resourceUrl);
            
            // 如果是CSS文件，应用备用样式
            if (resource.tagName === 'LINK' && resource.rel === 'stylesheet') {
                applyFallbackStyles();
            }
            
            // 如果是JS文件，尝试使用本地版本
            if (resource.tagName === 'SCRIPT') {
                loadLocalScript(resourceUrl);
            }
        }
    }
    
    // 应用备用样式
    function applyFallbackStyles() {
        // 检查是否已经加载了备用CSS
        if (!document.querySelector('link[href*="offline.css"]')) {
            const fallbackCSS = document.createElement('link');
            fallbackCSS.rel = 'stylesheet';
            fallbackCSS.href = '/static/css/offline.css';
            document.head.appendChild(fallbackCSS);
        }
    }
    
    // 加载本地脚本
    function loadLocalScript(originalUrl) {
        let localUrl = null;
        
        // 映射外部URL到本地文件
        if (originalUrl.includes('jquery')) {
            localUrl = '/static/js/jquery.min.js';
        } else if (originalUrl.includes('bootstrap')) {
            localUrl = '/static/js/bootstrap.min.js';
        } else if (originalUrl.includes('popper')) {
            localUrl = '/static/js/popper.min.js';
        }
        
        if (localUrl) {
            const script = document.createElement('script');
            script.src = localUrl;
            script.onload = function() {
                console.log('本地脚本加载成功:', localUrl);
            };
            script.onerror = function() {
                console.error('本地脚本加载失败:', localUrl);
            };
            document.head.appendChild(script);
        }
    }
    
    // 重试失败的资源
    function retryFailedResources() {
        if (failedResources.size > 0) {
            console.log('尝试重新加载失败的资源...');
            failedResources.clear();
            location.reload();
        }
    }
    
    // 检测资源加载状态
    function checkResourceLoading() {
        // 检查Bootstrap CSS
        const bootstrapCSS = document.querySelector('link[href*="bootstrap"]');
        if (bootstrapCSS) {
            bootstrapCSS.addEventListener('error', handleResourceError);
        }
        
        // 检查jQuery
        const jqueryScript = document.querySelector('script[src*="jquery"]');
        if (jqueryScript) {
            jqueryScript.addEventListener('error', handleResourceError);
        }
        
        // 检查Bootstrap JS
        const bootstrapJS = document.querySelector('script[src*="bootstrap"]');
        if (bootstrapJS) {
            bootstrapJS.addEventListener('error', handleResourceError);
        }
    }
    
    // 初始化
    function init() {
        // 创建离线指示器
        createOfflineIndicator();
        
        // 检查初始网络状态
        checkOnlineStatus();
        
        // 检查资源加载状态
        setTimeout(checkResourceLoading, 100);
        
        // 监听所有资源加载错误
        document.addEventListener('error', function(event) {
            if (event.target.tagName === 'LINK' || event.target.tagName === 'SCRIPT') {
                handleResourceError(event);
            }
        }, true);
    }
    
    // 页面加载完成后初始化
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
    // 暴露给全局
    window.OfflineHandler = {
        checkOnlineStatus: checkOnlineStatus,
        retryFailedResources: retryFailedResources,
        applyFallbackStyles: applyFallbackStyles
    };
    
})();

// 简化的jQuery功能（当jQuery加载失败时使用）
if (typeof $ === 'undefined') {
    console.log('jQuery未加载，使用简化版本');
    
    // 简化的选择器
    window.$ = function(selector) {
        if (typeof selector === 'string') {
            return document.querySelectorAll(selector);
        }
        return selector;
    };
    
    // 简化的AJAX
    $.post = function(url, data, callback) {
        const xhr = new XMLHttpRequest();
        xhr.open('POST', url, true);
        xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
        
        xhr.onreadystatechange = function() {
            if (xhr.readyState === 4) {
                if (xhr.status === 200) {
                    try {
                        const response = JSON.parse(xhr.responseText);
                        callback(response);
                    } catch (e) {
                        callback({ success: false, error: '响应格式错误' });
                    }
                } else {
                    callback({ success: false, error: '请求失败' });
                }
            }
        };
        
        // 将数据转换为表单格式
        const formData = [];
        for (const key in data) {
            formData.push(encodeURIComponent(key) + '=' + encodeURIComponent(data[key]));
        }
        
        xhr.send(formData.join('&'));
    };
    
    $.get = function(url, callback) {
        const xhr = new XMLHttpRequest();
        xhr.open('GET', url, true);
        
        xhr.onreadystatechange = function() {
            if (xhr.readyState === 4) {
                if (xhr.status === 200) {
                    try {
                        const response = JSON.parse(xhr.responseText);
                        callback(response);
                    } catch (e) {
                        callback({ success: false, error: '响应格式错误' });
                    }
                } else {
                    callback({ success: false, error: '请求失败' });
                }
            }
        };
        
        xhr.send();
    };
    
    // 简化的DOM操作
    $.fn = {
        on: function(event, handler) {
            this.forEach(function(element) {
                element.addEventListener(event, handler);
            });
            return this;
        },
        
        hide: function() {
            this.forEach(function(element) {
                element.style.display = 'none';
            });
            return this;
        },
        
        show: function() {
            this.forEach(function(element) {
                element.style.display = '';
            });
            return this;
        },
        
        val: function(value) {
            if (value !== undefined) {
                this.forEach(function(element) {
                    element.value = value;
                });
                return this;
            } else {
                return this[0] ? this[0].value : '';
            }
        },
        
        text: function(value) {
            if (value !== undefined) {
                this.forEach(function(element) {
                    element.textContent = value;
                });
                return this;
            } else {
                return this[0] ? this[0].textContent : '';
            }
        },
        
        html: function(value) {
            if (value !== undefined) {
                this.forEach(function(element) {
                    element.innerHTML = value;
                });
                return this;
            } else {
                return this[0] ? this[0].innerHTML : '';
            }
        },
        
        prop: function(property, value) {
            if (value !== undefined) {
                this.forEach(function(element) {
                    element[property] = value;
                });
                return this;
            } else {
                return this[0] ? this[0][property] : '';
            }
        },
        
        attr: function(attribute, value) {
            if (value !== undefined) {
                this.forEach(function(element) {
                    element.setAttribute(attribute, value);
                });
                return this;
            } else {
                return this[0] ? this[0].getAttribute(attribute) : '';
            }
        },
        
        append: function(content) {
            this.forEach(function(element) {
                element.insertAdjacentHTML('beforeend', content);
            });
            return this;
        },
        
        after: function(content) {
            this.forEach(function(element) {
                element.insertAdjacentHTML('afterend', content);
            });
            return this;
        },
        
        find: function(selector) {
            const results = [];
            this.forEach(function(element) {
                const found = element.querySelectorAll(selector);
                for (let i = 0; i < found.length; i++) {
                    results.push(found[i]);
                }
            });
            return results;
        }
    };
    
    // 扩展jQuery对象
    for (const key in $.fn) {
        if ($.fn.hasOwnProperty(key)) {
            const method = $.fn[key];
            $.fn[key] = function() {
                const args = Array.prototype.slice.call(arguments);
                return method.apply(this, args);
            };
        }
    }
} 