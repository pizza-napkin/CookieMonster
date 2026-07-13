class CookieMonster:
    def __init__(self, url: str):
        self.target_url = url # WE SHALL STEAL, THE COOKIES (aka in ts URL we yoink cookies)
        self.cookies = None
        self.redirect = None
        self.ses = requests.Session()
    
    # tag mixed w/ an ID/CLASS would speed up the process of yoinking cookies (else u have to wait 30s)
    # this is internal so the user doesn't have to do like asyncio jutusu to run ts lmao
    async def get_cookie_internal(self, tag: str=None, ID: str=None, CLASS: str=None) -> list:

        opts = ChromiumOptions()

        async with Chrome(options=opts) as browser:
            tab = await browser.start()

            await tab.enable_auto_solve_cloudflare_captcha()
            await tab.go_to(self.target_url)

            if ID is not None:
                await tab.find(
                    tag_name=tag,
                    id=ID,
                    timeout=30,
                )
            elif CLASS is not None:
                await tab.find(
                    tag_name=tag,
                    class_name=CLASS,
                    timeout=30,
                )
            else: await asyncio.sleep(30)
            await tab.disable_auto_solve_cloudflare_captcha()

            cookies = await tab.get_cookies()
            user_agent = await tab.execute_script("return navigator.userAgent")
            redirect = await tab.current_url

            await browser.stop()
        
        return cookies, user_agent, redirect
    
    # MUST run ts, u get cookies from it :3
    def get_cookies(self, tag: str, ID=None, CLASS=None) -> list:
        cookies, ua, redirect = asyncio.run(self.get_cookie_internal(tag, ID, CLASS))
        self.cookies = {i['name']: i['value'] for i in cookies}
        self.headers = {
            "User-Agent": ua['result']['result']['value'],
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Sec-Ch-Ua-Mobile": "?0",
        }
        self.redirect = redirect
    
    # makes the request W/ cookies we yoinked fr
    def milk(self, url: str) -> requests.Response:
        if self.cookies is None:
            raise Exception("Cookies not set. Call get_cookies() first.")
        
        return self.ses.get(url, cookies=self.cookies, headers=self.headers, impersonate="chrome120")
