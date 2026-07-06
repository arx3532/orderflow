# Run this in your project root or separately
import hashlib
import base64
import os

code_verifier = base64.urlsafe_b64encode(os.urandom(32)).rstrip(b'=').decode('utf-8')
code_challenge = base64.urlsafe_b64encode(
    hashlib.sha256(code_verifier.encode('utf-8')).digest()
).rstrip(b'=').decode('utf-8')

print("code_verifier:", code_verifier)
print("code_challenge:", code_challenge)


'''
access_token : eyJLSUQiOiI3a2w4OW0wbi0yb3BxLTVyNnMtOHQ5MS11MnYzNHd4NTZ5ejAiLCJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJvem9uZS1jeCIsInN1YiI6IjIwNjUzNzI3MiIsImV4cCI6MTc 
               4MjgwMTU3OCwiaWF0IjoxNzgyMzY5NTc4LCJ1c2VyX3Bvb2wiOiJVU0VSX1BPT0xfSU5WQUxJRCIsInRpZCI6ImZmM2E5NjczLWI4NDgtNGYyNy1iMTM3LTBhODgxZGZkZjg5MiIsInRva2VuIjoiYTgzYzY 
               wZDItYjgyYy00OTg4LTlmY2YtZDAyN2M1MWU4OTY4ZjI1N2FhMTktNDE2OC00OTI5LTk1OTgtYmQ2ZDNjN2YzNGNiIiwic2Vzc2lvbl9pZCI6Im45c1RNN3U3ditxekd1SXVHSGFzNFEiLCJzaWF0IjoxNzg 
               yMzY5NTc4fQ.WMazurQjHDiP8AZB_fMcH3hgAuJjgnQ10t8dJYmPHtciY75I2kMl_zLgoLG2jae1WDGlnkYeyBU2f-vhoK30ZfyGTXol9Uih034ikm6maeqbEcf_Uhsgk4C2fshn8axw-LNxvQ0zrydMWR9V 
               WNFe6s23ulEquXV5fX2xv3QJP4FP7Kj88ub7AmmzklM_ggKnSkalBf_uTt1tCKYTLM9Oisf9KwQCg_VgImMFpQKffkv7cnZAwQJJzbWRV02OJ4KAUEQRAppcrlpqpDNgVZbA3FxzOOG0ksmlZW63b25vRZFS 
               dvfmHZ_jraXGFlfuZZQ7137ckj6c2KforesQGrim-w
token_type   : Bearer
expires_in   : 432000
user_id      : 206537272
tid          : ff3a9673-b848-4f27-b137-0a881dfdf892
'''