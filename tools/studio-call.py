import argparse,json
from pathlib import Path
from urllib.request import Request,urlopen
parser=argparse.ArgumentParser();parser.add_argument('tool');parser.add_argument('--file',type=Path);parser.add_argument('--body',default='{}');parser.add_argument('--out',type=Path);args=parser.parse_args()
body=json.loads(args.body)
if args.file:body['code']=args.file.read_text(encoding='utf-8')
body.setdefault('instance_id','instance:qia-6lf')
token=Path(r'C:\Users\larp\.robloxstudio-mcp\auth-token').read_text().strip()
request=Request('http://127.0.0.1:58741/mcp/'+args.tool,data=json.dumps(body).encode(),headers={'X-MCP-Auth':token,'Content-Type':'application/json'})
with urlopen(request,timeout=90)as f:r=json.load(f)
if args.out:args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(json.dumps(r,indent=2),encoding='utf-8')
print(json.dumps(r)if not args.out else json.dumps({'saved':str(args.out),'success':r.get('success'),'keys':list(r)}))
