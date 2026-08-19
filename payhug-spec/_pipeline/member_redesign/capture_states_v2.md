# 회원관리 프로토타입 v2 51상태 → Figma 네이티브 임포트 로그 (2026-08-19)

- 파일: Tcf69tIciGxmlqCIuRb0iI / 임포트 페이지: 2822:2294 ([정산_정책 백업])
- 서버: http://localhost:8902/index.html?state=<id> (v2 정책 반영판, 폭 1920, STATE:<id>:READY)
- 방식: generate_figma_design captureId 발급 → figcap_state.sh 헤드리스 제출 → 폴링(최대 24회)

| state | url | captureId | node_id | w×h | 비고 |
|---|---|---|---|---|---|
| A1 | ?state=A1 | b4b29608-59f3-4509-b14f-02e31ce26640 | 2933:2 | 1922×1513 | STATE:A1:READY |
| A2 | ?state=A2 | a03c1185-e99e-4af1-9444-421ee727555c | 2934:2 | 1922×1513 | STATE:A2:READY |
| A3 | ?state=A3 | 32d48ffd-3fa6-4027-aeac-3374570aac6d | 2935:2 | 1922×1513 | STATE:A3:READY |
| A4 | ?state=A4 | 9b668e97-e2c3-4b4e-a24e-b123b29024ec | 2936:2 | 1922×1513 | STATE:A4:READY |
| A5 | ?state=A5 | 80f10c68-e5ec-4def-b140-cc1b5797768e | 2937:2 | 1922×1513 | STATE:A5:READY |
| A6 | ?state=A6 | 2acb913f-dc55-4e09-b088-b11f623f7a24 | 2938:2 | 1922×1513 | STATE:A6:READY |
| A7 | ?state=A7 | 4bca5c01-21e4-4e1b-afa8-24590b15cfe5 | 2939:2 | 1922×1513 | STATE:A7:READY |
| B1 | ?state=B1 | cca3325e-3802-40f5-ba3e-340f611c1d6b | 2940:2 | 1922×1535 | STATE:B1:READY |
| B2 | ?state=B2 | e970df63-604e-4e35-b305-26a779d791f3 | 2941:2 | 1922×1535 | STATE:B2:READY |
| B3 | ?state=B3 | 4359267f-10ce-457f-9f39-6ee2a7416343 | 2942:2 | 1922×1535 | STATE:B3:READY |
| B4 | ?state=B4 | 375e74bb-64b5-4e59-97d5-b1d043ed2a58 | 2943:2 | 1922×1535 | STATE:B4:READY |
| B5 | ?state=B5 | 18c93004-7e4e-4e8a-b25c-ed601a14a297 | 2944:2 | 1922×1535 | STATE:B5:READY |
| B6 | ?state=B6 | f94b8dcf-7a43-47ee-8911-e913ba84f0ca | 2945:2 | 1922×1513 | STATE:B6:READY |
| B7 | ?state=B7 | 076645c0-0bd5-443b-b1cd-40e936c0627c | 2946:2 | 1922×1579 | STATE:B7:READY |
| B8 | ?state=B8 | e8a0209d-ed03-470a-8500-64f42787d39f | 2947:2 | 1922×1513 | STATE:B8:READY |
| B9 | ?state=B9 | 58e50a03-9591-4efa-80a6-4d2882447215 | 2948:2 | 1922×1513 | STATE:B9:READY |
| B10 | ?state=B10 | 15e6fbeb-1c44-481d-bb99-ecfe942309c7 | 2949:2 | 1922×1513 | STATE:B10:READY |
| C1 | ?state=C1 | c28fc574-6ee7-4d62-87c4-2d1c2b04ec8b | 2950:2 | 1922×1550 | STATE:C1:READY |
| C2 | ?state=C2 | fce8a479-095f-4dd4-8754-4a8924c809d4 | 2951:2 | 1922×1550 | STATE:C2:READY |
| C3 | ?state=C3 | cd2e0a07-1866-4c20-bc9b-e5deaa7355ce | 2952:2 | 1922×1550 | STATE:C3:READY |
| C4 | ?state=C4 | f9011f74-5ff7-4df0-a044-987028efcaf6 | 2953:2 | 1922×1550 | STATE:C4:READY |
| C5 | ?state=C5 | 6e7b1cae-501d-4bb4-a24e-44c02c69ef4a | 2954:2 | 1922×1550 | STATE:C5:READY |
| C6 | ?state=C6 | a9c033a7-846f-4ad0-b578-407ee26a63bb | 2955:2 | 1922×1513 | STATE:C6:READY |
| D1 | ?state=D1 | 5588a6fb-2309-46ca-a5a9-76a4fb28b081 | 2956:2 | 1922×1554 | STATE:D1:READY |
| D2 | ?state=D2 | a95671ef-eca7-4808-bdcf-1ecb33d865af | 2957:2 | 1922×1554 | STATE:D2:READY |
| D3 | ?state=D3 | d8d6c1e6-8549-45dc-81c7-3a5bb8be6e34 | 2958:2 | 1922×1569 | STATE:D3:READY |
| D4 | ?state=D4 | 8d55f391-d8e4-49bf-96f5-8876a7f9c90d | 2959:2 | 1922×1741 | STATE:D4:READY |
| D5 | ?state=D5 | fd97e28b-64f3-4b2c-a796-cbb0a14918f5 | 2960:2 | 1922×1615 | STATE:D5:READY |
| D6 | ?state=D6 | ffb70339-0868-4b26-bcf0-d36ae1443351 | 2961:2 | 1922×1535 | STATE:D6:READY |
| D7 | ?state=D7 | 3e023a09-3a2d-4910-b980-ebd6dfad9e25 | 2962:2 | 1922×1535 | STATE:D7:READY |
| E1 | ?state=E1 | 048bb0e0-9d2b-4667-af11-01de0781eaf7 | 2963:2 | 1922×1685 | STATE:E1:READY |
| E2 | ?state=E2 | 82280d63-1de4-409d-82ae-8f454a8d5c80 | 2964:2 | 1922×1685 | STATE:E2:READY |
| E3 | ?state=E3 | 4e5284bf-a5cc-429d-825c-516cf591f738 | 2965:2 | 1922×1513 | STATE:E3:READY |
| E4 | ?state=E4 | 4cc10d4e-8775-4f5c-8ee3-68dab4c486ca | 2966:2 | 1922×1685 | STATE:E4:READY |
| F1 | ?state=F1 | 9475a02b-f1c7-4947-8808-098cd34068c8 | 2967:2 | 1922×1513 | STATE:F1:READY |
| F2 | ?state=F2 | b739a423-d44b-4737-b620-10d9805e71f8 | 2968:2 | 1922×1513 | STATE:F2:READY |
| F3 | ?state=F3 | 39629ac8-8b95-4277-bebe-06b77da5b228 | 2969:2 | 1922×1513 | STATE:F3:READY |
| F4 | ?state=F4 | 67f0ec81-5591-40c7-82cd-157ccccc5e9b | 2970:2 | 1922×1513 | STATE:F4:READY |
| F5 | ?state=F5 | 759034c4-adeb-44c1-b597-0da8b9a6181e | 2971:2 | 1922×1513 | STATE:F5:READY |
| F6 | ?state=F6 | 7be70204-f658-4b77-a1c1-60ea02541a99 | 2972:2 | 1922×1513 | STATE:F6:READY |
| G1 | ?state=G1 | 45d21d1d-fcb4-47cd-8c56-d75af07d1451 | 2973:2 | 1922×1513 | STATE:G1:READY |
| G2 | ?state=G2 | 086ce954-0bca-4f1c-ad99-a53de6add0ae | 2974:2 | 1922×1513 | STATE:G2:READY |
| G3 | ?state=G3 | 645ba7c2-a3dd-4e29-a501-c4132b704b27 | 2975:2 | 1922×1513 | STATE:G3:READY |
| G4 | ?state=G4 | 95fb0221-5b00-4377-a115-03a7ec3c4506 | 2976:2 | 1922×1965 | STATE:G4:READY |
| G5 | ?state=G5 | 69934321-f0f3-4941-929d-48b3733858a5 | 2977:2 | 1922×1550 | STATE:G5:READY |
| G6 | ?state=G6 | 54bd4af7-5139-40a9-a6d4-12cbd7002bca | 2978:2 | 1922×1513 | STATE:G6:READY |
| H1 | ?state=H1 | f17c8242-b9bc-4f9b-bf01-2cf5dc356740 | 2979:2 | 1922×1513 | STATE:H1:READY |
| H2 | ?state=H2 | 3ffc2244-df9d-40e5-bef4-162d136e74d1 | 2980:2 | 1922×1513 | STATE:H2:READY |
| H3 | ?state=H3 | 9bb7f83f-1abc-47a6-a4d4-8ea9215192d8 | 2981:2 | 1922×1513 | STATE:H3:READY |
| H4 | ?state=H4 | 5455cb50-9780-4047-ab58-f3189138fe87 | 2982:2 | 1922×1513 | STATE:H4:READY |
| H5 | ?state=H5 | cfa91037-5a47-4296-b121-1a113e33b670 | 2983:2 | 1922×1535 | STATE:H5:READY |

## 결과 요약 (2026-08-19, v2)
- 51/51 성공, 실패·재시도 0. captureId 한도 초과 없음.
- 폴링 중 소켓 오류 1회(G6) — 동일 captureId 재폴링으로 즉시 해소(재캡처 아님).
- 전 프레임 폭 1922 (뷰포트 1922 지정). 높이 기본 1513, 예외: B1~B5/D6/D7/H5=1535, B7=1579, C1~C5/G5=1550, D1/D2=1554, D3=1569, D4=1741, D5=1615, E1/E2/E4=1685, G4=1965.
- 노드ID 2933:2~2983:2 연속(결번 없음). 프레임명 STATE:<id>:READY로 상태 일치 검증 완료.
- 배치: 페이지 2822:2294 x=123359부터 40px 간격 가로 나열, y=0. 이동·조립은 후속 몫.
- 맵: state_import_map_v2.json (node_id/width/height/page/x/y).
