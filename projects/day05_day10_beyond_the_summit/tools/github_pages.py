"""Authorized Pages administration using existing Git Credential Manager.

Credentials stay in subprocess/Python memory; never printed, saved, or placed in
arguments. GitHub connector currently has no Pages settings/dispatch capability.
"""
import argparse,json,os,subprocess,urllib.request,urllib.error

BASE='https://api.github.com/repos/mmirshod/30daymapchallenge-2026'

def credential():
    env={**os.environ,'GIT_TERMINAL_PROMPT':'0','GCM_INTERACTIVE':'never'}
    result=subprocess.run(['git','credential','fill'],input='protocol=https\nhost=github.com\n\n',text=True,capture_output=True,env=env,check=False)
    if result.returncode:raise RuntimeError('Existing GitHub credential unavailable; no credential details printed')
    values=dict(line.split('=',1) for line in result.stdout.splitlines() if '=' in line)
    if not values.get('password'):raise RuntimeError('No existing GitHub token returned')
    return values['password']

def main():
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['status','configure','dispatch','runs','run','build']);parser.add_argument('--run-id',type=int)
    args=parser.parse_args();token=credential()
    def api(path='',method='GET',data=None):
        req=urllib.request.Request(BASE+path,method=method,data=json.dumps(data).encode() if data is not None else None,
            headers={'Authorization':'Bearer '+token,'Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28','User-Agent':'BeyondTheSummit-Publication','Content-Type':'application/json'})
        try:
            with urllib.request.urlopen(req,timeout=45) as r:
                raw=r.read();return json.loads(raw) if raw else {'http_status':r.status}
        except urllib.error.HTTPError as e:
            body=json.loads(e.read() or b'{}');raise RuntimeError(f'GitHub API {method} {path}: {e.code}, '+body.get('message','request failed')) from None
    if args.action=='status':
        repo=api();pages=api('/pages')
        print(json.dumps({'repository':repo['full_name'],'default_branch':repo['default_branch'],'pages':pages},indent=2))
    elif args.action=='configure':
        result=api('/pages','PUT',{'build_type':'workflow'})
        print(json.dumps(result,indent=2))
    elif args.action=='dispatch':
        print(json.dumps(api('/actions/workflows/pages.yml/dispatches','POST',{'ref':'main'}),indent=2))
    elif args.action=='runs':
        rows=api('/actions/runs?per_page=5')['workflow_runs']
        print(json.dumps([{k:r.get(k) for k in ['id','head_sha','status','conclusion','html_url','created_at','event']} for r in rows],indent=2))
    elif args.action=='build':
        print(json.dumps(api('/pages/builds/latest'),indent=2))
    else:
        if not args.run_id:parser.error('--run-id required')
        r=api('/actions/runs/'+str(args.run_id));jobs=api('/actions/runs/'+str(args.run_id)+'/jobs')['jobs']
        print(json.dumps({'run':{k:r.get(k) for k in ['id','head_sha','status','conclusion','html_url']},'jobs':[{'name':j['name'],'status':j['status'],'conclusion':j['conclusion'],'steps':j.get('steps',[])} for j in jobs]},indent=2))

if __name__=='__main__':main()
