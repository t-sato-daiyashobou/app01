import ssl
import requests
import urllib3
from bs4 import BeautifulSoup

if __name__ == "__main__":
    ctx = ssl.create_default_context()
    ctx.set_ciphers("AESGCM")

    adapter = requests.adapters.HTTPAdapter()
    adapter.poolmanager = urllib3.PoolManager(
        ssl_version=ssl.PROTOCOL_TLSv1_2, ssl_context=ctx
    )

    session = requests.Session()
    session.verify = True
    session.mount("https://", adapter)

    url = "https://inter-consistent2.kuronekoyamato.co.jp/consistent2/cts"
    
    tracking_number = "437111342076" 
    
    payload = f"""<?xml version="1.0" encoding="UTF-8"?>    
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
                                    <伝票番号>{tracking_number}</伝票番号>
                                </伝票番号検索>
                            </検索条件>
                        </問合せ要求>
                    ]]>
                </XMLData>
            </ns1:provideXMLTraceService>
        </soapenv:Body>
    </soapenv:Envelope>"""
    headers = {
        "Content-Type": "application/soap+xml; charset=UTF-8",
        "SOAPAction": "provideXMLTraceService",
    }

    with session.post(url, headers=headers, data=payload) as r:
        soap_response = BeautifulSoup(r.text, "xml")
        data = BeautifulSoup(soap_response.text, "xml")

        for i in data.select("検索キータイトル1,検索キータイトル2"):
            print(i.prettify())
