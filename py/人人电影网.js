var rule = {
    title: '人人电影网',
    host: 'https://www.rrdynb.com',
    homeUrl: '/',
    url: '/fyclass_fypage.html?',
    filter_url: '{{fl.class}}',
    filter: {},
    searchUrl: '/plus/search.php?q=**&pagesize=10&submit=',
    searchable: 2,
    quickSearch: 1,
    filterable: 0,
    headers: {
        'User-Agent': 'PC_UA',
        'Cookie': ''
    },
    timeout: 5000,
    class_name: '影视&电视剧&老电影&动漫',
    class_url: 'movie/list_2&dianshiju/list_6&zongyi/list_10&dongman/list_13',
    play_parse: true,
    play_json: [{
        re: '*',
        json: {
            parse: 0,
            jx: 0
        }
    }],
    lazy: "js:\n        input = 'push://' + input;\n    ",
    limit: 6,
    推荐: '',
    一级: 'li:has(img);img&&alt;img&&data-original;;a&&href',
    二级: {
        title: "h1&&Text",
        img: "img&&src",
        desc: ".info:eq(0)&&Text",
        content: ".content&&Text",
        tabs: `js:
            pdfh = jsp.pdfh;
            pdfa = jsp.pdfa;
            TABS = [];
            let d = pdfa(html, 'span a');
            let hasBaidu = false;
            let hasQuark = false;
            
            d.forEach(function(it) {
                let burl = pdfh(it, 'a&&href');
                if (burl.includes("pan.baidu.com/s/")) {
                    hasBaidu = true;
                } else if (burl.includes("pan.quark.cn/s/")) {
                    hasQuark = true;
                }
            });
            
            if (hasBaidu) TABS.push("百度网盘");
            if (hasQuark) TABS.push("夸克网盘");
            
            log('生成TABS: ' + JSON.stringify(TABS));`,
        lists: `js:
            pdfh = jsp.pdfh;
            pdfa = jsp.pdfa;
            LISTS = [];
            let d = pdfa(html, 'span a');
            
            function extractCode(title, patterns) {
                for (let pattern of patterns) {
                    const match = title.match(pattern);
                    if (match && match[1]) {
                        return match[1];
                    }
                }
                return null;
            }
            
            let baiduList = [];
            let quarkList = [];
            
            d.forEach(function(it) {
                let burl = pdfh(it, 'a&&href');
                let title = pdfh(it, 'a&&Text');
                
                if (burl.includes("pan.baidu.com/s/")) {
                    const baiduPatterns = [
                        /(?:提取码|密码|验证码|code|pwd|码)[：:\s]*(\w{4})/i,
                        /(?:\b|\s)(\w{4})(?=提取|百度|网盘|分享|$)/i,
                        /[\s\[](\w{4})[\s\]]/,
                        /\b(\w{4})\b/
                    ];
                    const code = extractCode(title, baiduPatterns);
                    if (code) {
                        burl += '#' + code;
                        log('百度网盘提取码识别成功: ' + code);
                    }
                    baiduList.push(title + '$' + burl);
                } 
                else if (burl.includes("pan.quark.cn/s/")) {
                    const quarkPatterns = [
                        /(?:密码|pwd)[：:\s]*(\w{4,8})/i,
                        /(?:\b|\s)(\w{4,8})(?=提取|夸克|网盘|分享|$)/i,
                        /[\s\[](\w{4,8})[\s\]]/,
                        /\b(\w{4,8})\b/
                    ];
                    const code = extractCode(title, quarkPatterns);
                    if (code) {
                        burl += '#' + code;
                        log('夸克网盘密码识别成功: ' + code);
                    }
                    quarkList.push(title + '$' + burl);
                }
            });
            
            if (baiduList.length > 0) LISTS.push(baiduList);
            if (quarkList.length > 0) LISTS.push(quarkList);`,
    },
    搜索: 'li:has(img);h2&&Text;img&&data-original;.tags&&Text;a&&href',
};