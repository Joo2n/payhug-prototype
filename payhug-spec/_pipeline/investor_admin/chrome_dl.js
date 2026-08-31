// 헤드리스 크롬이 파일을 사용자의 다운로드 폴더에 떨구지 않게 막는다.
//
// 화면 검증기는 `엑셀 다운로드`·`증명서 내려받기` 같은 링크를 실제로 눌러 본다.
// 크롬은 받을 자리를 안 정해 주면 기본값인 ~/Downloads 로 보낸다. 검증기를 한 번
// 돌릴 때마다 사용자 폴더에 파일이 쌓인다.
//
//   const DL = require('./chrome_dl');
//   const dl = DL.dir();                     // 임시 받을 자리
//   spawn(CHROME, DL.args(dl).concat([...]))
//
// `--user-data-dir` 을 이미 쓰는 스크립트는 그 경로를 넘긴다.
//   spawn(CHROME, DL.args(dl, prof).concat([...]))
const fs = require('fs');
const os = require('os');
const path = require('path');

function dir() {
  return fs.mkdtempSync(path.join(os.tmpdir(), 'phdl-'));
}

function args(downloadDir, profileDir) {
  const prof = profileDir || fs.mkdtempSync(path.join(os.tmpdir(), 'phprof-'));
  const def = path.join(prof, 'Default');
  fs.mkdirSync(def, { recursive: true });
  const pref = path.join(def, 'Preferences');
  let cur = {};
  try { cur = JSON.parse(fs.readFileSync(pref, 'utf8')); } catch (e) { cur = {}; }
  cur.download = Object.assign({}, cur.download, {
    default_directory: downloadDir,
    prompt_for_download: false,
    directory_upgrade: true,
  });
  cur.savefile = Object.assign({}, cur.savefile, { default_directory: downloadDir });
  fs.writeFileSync(pref, JSON.stringify(cur));
  return ['--user-data-dir=' + prof];
}

// CDP 를 이미 쓰는 스크립트용. 연결 직후 한 번 부른다.
async function behavior(send, downloadDir) {
  await send('Browser.setDownloadBehavior', { behavior: 'allow', downloadPath: downloadDir });
}

// 임시 받을 자리를 지운다.
function clean(downloadDir) {
  try { fs.rmSync(downloadDir, { recursive: true, force: true }); } catch (e) {}
}

module.exports = { dir, args, behavior, clean };
