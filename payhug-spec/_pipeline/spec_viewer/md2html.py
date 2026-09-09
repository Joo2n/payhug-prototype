import re, html, json, os, datetime

def esc(t):
    return html.escape(t, quote=False)

def inline(t):
    # 코드 먼저 뽑아내 보호
    stash = []
    def keep(m):
        stash.append(m.group(1))
        return f"\x00{len(stash)-1}\x00"
    t = re.sub(r'`([^`]+)`', keep, t)
    t = esc(t)
    t = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'(?<![\w*])\*([^*\n]+)\*(?![\w*])', r'<em>\1</em>', t)
    t = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank" rel="noopener">\1</a>', t)
    def back(m):
        return '<code>' + esc(stash[int(m.group(1))]) + '</code>'
    t = re.sub(r'\x00(\d+)\x00', back, t)
    return t

def split_row(line):
    s = line.strip()
    if s.startswith('|'): s = s[1:]
    if s.endswith('|'): s = s[:-1]
    return [c.strip() for c in s.split('|')]

def convert(md):
    lines = md.split('\n')
    out, i, n = [], 0, len(lines)
    while i < n:
        ln = lines[i]
        s = ln.strip()

        if s.startswith('```'):
            lang = s[3:].strip()
            i += 1
            buf = []
            while i < n and not lines[i].strip().startswith('```'):
                buf.append(lines[i]); i += 1
            i += 1
            out.append(f'<pre class="code"><code>{esc(chr(10).join(buf))}</code></pre>')
            continue

        if re.fullmatch(r'(-{3,}|\*{3,}|_{3,})', s):
            out.append('<hr>'); i += 1; continue

        m = re.match(r'^(#{1,6})\s+(.*)$', s)
        if m:
            lv = len(m.group(1))
            txt = inline(m.group(2))
            anchor = re.sub(r'[^0-9a-zA-Z가-힣]+', '-', m.group(2)).strip('-')
            out.append(f'<h{lv} id="h-{anchor}">{txt}</h{lv}>')
            i += 1; continue

        # 표
        if s.startswith('|') and i + 1 < n and re.match(r'^\|?[\s:\-\|]+\|?$', lines[i+1].strip()) and '-' in lines[i+1]:
            head = split_row(lines[i])
            i += 2
            body = []
            while i < n and lines[i].strip().startswith('|'):
                body.append(split_row(lines[i])); i += 1
            th = ''.join(f'<th>{inline(c)}</th>' for c in head)
            trs = []
            for r in body:
                while len(r) < len(head): r.append('')
                trs.append('<tr>' + ''.join(f'<td>{inline(c)}</td>' for c in r[:len(head)]) + '</tr>')
            out.append(f'<div class="tw"><table><thead><tr>{th}</tr></thead><tbody>{"".join(trs)}</tbody></table></div>')
            continue

        if s.startswith('>'):
            buf = []
            while i < n and lines[i].strip().startswith('>'):
                buf.append(lines[i].strip()[1:].strip()); i += 1
            out.append('<blockquote>' + '<br>'.join(inline(b) for b in buf) + '</blockquote>')
            continue

        # 리스트 (들여쓰기 depth 유지)
        if re.match(r'^\s*([-*+]|\d+\.)\s+', ln):
            items = []
            while i < n and re.match(r'^\s*([-*+]|\d+\.)\s+', lines[i]):
                raw = lines[i]
                indent = len(raw) - len(raw.lstrip())
                mm = re.match(r'^\s*([-*+]|\d+\.)\s+(.*)$', raw)
                ordered = bool(re.match(r'\d+\.', mm.group(1)))
                items.append((indent // 2, ordered, mm.group(2)))
                i += 1
            # depth 기반 중첩
            htmlbuf, stack = [], []
            for depth, ordered, txt in items:
                while len(stack) > depth + 1:
                    htmlbuf.append('</ul>' if not stack[-1] else '</ol>'); stack.pop()
                if len(stack) < depth + 1:
                    while len(stack) < depth + 1:
                        htmlbuf.append('<ol>' if ordered else '<ul>'); stack.append(ordered)
                htmlbuf.append(f'<li>{inline(txt)}</li>')
            while stack:
                htmlbuf.append('</ol>' if stack[-1] else '</ul>'); stack.pop()
            out.append(''.join(htmlbuf))
            continue

        if not s:
            i += 1; continue

        buf = []
        while i < n and lines[i].strip() and not lines[i].strip().startswith(('|', '>', '#', '```')) \
              and not re.match(r'^\s*([-*+]|\d+\.)\s+', lines[i]) \
              and not re.fullmatch(r'(-{3,}|\*{3,}|_{3,})', lines[i].strip()):
            buf.append(lines[i].strip()); i += 1
        if buf:
            out.append('<p>' + '<br>'.join(inline(b) for b in buf) + '</p>')
        else:
            i += 1
    return '\n'.join(out)

if __name__ == '__main__':
    import sys
    print(convert(open(sys.argv[1], encoding='utf-8').read()))
