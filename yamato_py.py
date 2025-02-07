import ssl
import time
from typing import List
import requests
import urllib3
from bs4 import BeautifulSoup

class YamatoTracking:
    def __init__(self):
        self.url = "https://inter-consistent2.kuronekoyamato.co.jp/consistent2/cts"
        self.session = self._create_session()
        self.headers = {
            "Content-Type": "application/soap+xml; charset=UTF-8",
            "SOAPAction": "provideXMLTraceService",
        }

    def _create_session(self) -> requests.Session:
        ctx = ssl.create_default_context()
        ctx.set_ciphers("AESGCM")
        
        adapter = requests.adapters.HTTPAdapter()
        adapter.poolmanager = urllib3.PoolManager(
            ssl_version=ssl.PROTOCOL_TLSv1_2, 
            ssl_context=ctx
        )
        
        session = requests.Session()
        session.verify = True
        session.mount("https://", adapter)
        return session

    def _create_tracking_xml(self, numbers: List[str]) -> str:
        tracking_xml = '\n'.join([
            f'<伝票番号>{num}</伝票番号>' 
            for num in numbers[:20]
        ])
        
        return f"""<?xml version="1.0" encoding="UTF-8"?>    
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
            <soapenv:Body>
                <ns1:provideXMLTraceService xmlns:ns1="urn:ClientReception">
                    <XMLData>
                        <![CDATA[
                            <問合せ要求>
                                <基本情報>
                                    <IPアドレス>193.186.4.181</IPアドレス>
                                    <顧客コード>022388898035</顧客コード>   
                                    <パスワード>a388898035</パスワード>
                                </基本情報>
                                <検索オプション>
                                    <検索区分>01</検索区分>
                                    <届け先情報表示フラグ>1</届け先情報表示フラグ>
                                </検索オプション>
                                <検索条件>
                                    <伝票番号検索>
                                        {tracking_xml}
                                    </伝票番号検索>
                                </検索条件>
                            </問合せ要求>
                        ]]>
                    </XMLData>
                </ns1:provideXMLTraceService>
            </soapenv:Body>
        </soapenv:Envelope>"""

    def _parse_tracking_response(self, response_text: str) -> List[dict]:
        """XMLレスポンスからトラッキング情報を抽出"""
        soap_response = BeautifulSoup(response_text, "xml")
        data = BeautifulSoup(soap_response.text, "xml")
        return data.select("検索キータイトル1,検索キータイトル2")

    def get_tracking_info(self, numbers: List[str]) -> List[dict]:
        results = []
        chunks = [numbers[i:i + 20] for i in range(0, len(numbers), 20)]
        
        for i, chunk in enumerate(chunks):
            if i > 0:
                time.sleep(5)
            
            try:
                payload = self._create_tracking_xml(chunk)
                with self.session.post(self.url, headers=self.headers, data=payload) as r:
                    r.raise_for_status()
                    results.extend(self._parse_tracking_response(r.text))
            except requests.RequestException as e:
                print(f"Error occurred: {e}")
                continue
        
        return results

if __name__ == "__main__":
    tracking = YamatoTracking()
    numbers = ["437340026476", "437334062023","437127410366","437111342076"]  # テスト用の伝票番号
    results = tracking.get_tracking_info(numbers)
    
    for result in results:
        print(result.prettify())
