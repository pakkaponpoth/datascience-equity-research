const fs = require('fs');
// ~SET100 constituents (ticker, Thai short name, English name, sector). Mock/demo universe.
const U = [
 ["KBANK","กสิกรไทย","Kasikornbank","Banking"],["SCB","เอสซีบี เอกซ์","SCB X","Banking"],["BBL","กรุงเทพ","Bangkok Bank","Banking"],
 ["KTB","กรุงไทย","Krung Thai Bank","Banking"],["TTB","ทีเอ็มบีธนชาต","TMBThanachart","Banking"],["TISCO","ทิสโก้","Tisco","Banking"],
 ["KKP","เกียรตินาคินภัทร","Kiatnakin Phatra","Banking"],["MTC","เมืองไทยแคปปิตอล","Muangthai Capital","Finance"],["SAWAD","ศรีสวัสดิ์","Srisawad","Finance"],
 ["TIDLOR","เงินติดล้อ","Ngern Tid Lor","Finance"],["KTC","เคทีซี","Krungthai Card","Finance"],["AEONTS","อิออน","Aeon Thana Sinsap","Finance"],
 ["JMT","เจเอ็มที","JMT Network","Finance"],["PTT","ปตท.","PTT","Energy"],["PTTEP","ปตท.สผ.","PTT E&P","Energy"],
 ["OR","โออาร์","PTT Oil & Retail","Energy"],["BCP","บางจาก","Bangchak","Energy"],["TOP","ไทยออยล์","Thai Oil","Energy"],
 ["IRPC","ไออาร์พีซี","IRPC","Energy"],["PTTGC","พีทีทีจีซี","PTT Global Chemical","Petrochem"],["SPRC","สตาร์ ปิโตรเลียม","Star Petroleum","Energy"],
 ["BANPU","บ้านปู","Banpu","Energy"],["GULF","กัลฟ์","Gulf Development","Utilities"],["GPSC","โกลบอล เพาเวอร์","Global Power Synergy","Utilities"],
 ["EA","พลังงานบริสุทธิ์","Energy Absolute","Utilities"],["BGRIM","บี.กริม เพาเวอร์","B.Grimm Power","Utilities"],["EGCO","เอ็กโก","Electricity Generating","Utilities"],
 ["RATCH","ราช กรุ๊ป","Ratch Group","Utilities"],["GUNKUL","กันกุล","Gunkul Engineering","Utilities"],["BGRIM2","บีซีพีจี","BCPG","Utilities"],
 ["ADVANC","เอไอเอส","Advanced Info Service","ICT"],["INTUCH","อินทัช","Intouch Holdings","ICT"],["TRUE","ทรู","True Corporation","ICT"],
 ["DELTA","เดลต้า อีเลคโทรนิคส์","Delta Electronics","Electronics"],["HANA","ฮานา","Hana Microelectronics","Electronics"],["KCE","เคซีอี","KCE Electronics","Electronics"],
 ["CPALL","ซีพี ออลล์","CP All","Commerce"],["CPAXT","ซีพี แอ็กซ์ตร้า","CP Axtra","Commerce"],["CRC","เซ็นทรัล รีเทล","Central Retail","Commerce"],
 ["HMPRO","โฮมโปร","Home Product Center","Commerce"],["COM7","คอมเซเว่น","Com7","Commerce"],["GLOBAL","สยามโกลบอลเฮ้าส์","Global House","Commerce"],
 ["DOHOME","ดูโฮม","Dohome","Commerce"],["BJC","เบอร์ลี่ ยุคเกอร์","Berli Jucker","Commerce"],["MEGA","เมก้า ไลฟ์ไซแอ็นซ์","Mega Lifesciences","Commerce"],
 ["CPF","ซีพีเอฟ","CP Foods","Food"],["TU","ไทยยูเนี่ยน","Thai Union","Food"],["MINT","ไมเนอร์ อินเตอร์เนชั่นแนล","Minor International","Tourism"],
 ["OSP","โอสถสภา","Osotspa","Food"],["CBG","คาราบาวกรุ๊ป","Carabao Group","Food"],["TFG","ไทยฟู้ดส์","Thaifoods Group","Food"],
 ["ITC","ไอ-เทล คอร์ปอเรชั่น","I-Tail","Food"],["SAPPE","เซ็ปเป้","Sappe","Food"],["TKN","เถ้าแก่น้อย","Taokaenoi","Food"],
 ["GFPT","จีเอฟพีที","GFPT","Food"],["LH","แลนด์ แอนด์ เฮ้าส์","Land & Houses","Property"],["AP","เอพี ไทยแลนด์","AP Thailand","Property"],
 ["SPALI","ศุภาลัย","Supalai","Property"],["SIRI","แสนสิริ","Sansiri","Property"],["QH","ควอลิตี้ เฮ้าส์","Quality Houses","Property"],
 ["ORIGIN","ออริจิ้น พร็อพเพอร์ตี้","Origin Property","Property"],["SC","เอสซี แอสเสท","SC Asset","Property"],["WHA","ดับบลิวเอชเอ","WHA Corporation","Property"],
 ["AMATA","อมตะ คอร์ปอเรชัน","Amata Corporation","Property"],["CPN","เซ็นทรัลพัฒนา","Central Pattana","Property"],["CENTEL","โรงแรมเซ็นทรัลพลาซา","Central Plaza Hotel","Tourism"],
 ["ERW","ดิ เอราวัณ กรุ๊ป","The Erawan Group","Tourism"],["SCC","ปูนซิเมนต์ไทย","Siam Cement","Materials"],["SCGP","เอสซีจี แพคเกจจิ้ง","SCG Packaging","Materials"],
 ["TASCO","ทิปโก้ แอสฟัลท์","Tipco Asphalt","Materials"],["DCC","ไดนาสตี้ เซรามิค","Dynasty Ceramic","Materials"],["TPIPP","ทีพีไอ โพลีน เพาเวอร์","TPI Polene Power","Utilities"],
 ["AOT","ท่าอากาศยานไทย","Airports of Thailand","Transportation"],["BEM","ทางด่วนและรถไฟฟ้ากรุงเทพ","Bangkok Expressway & Metro","Transportation"],["BTS","บีทีเอส กรุ๊ป","BTS Group","Transportation"],
 ["BDMS","กรุงเทพดุสิตเวชการ","Bangkok Dusit Medical","Healthcare"],["BH","บำรุงราษฎร์","Bumrungrad Hospital","Healthcare"],["BCH","บางกอก เชน ฮอสปิทอล","Bangkok Chain Hospital","Healthcare"],
 ["CHG","โรงพยาบาลจุฬารัตน์","Chularat Hospital","Healthcare"],["PR9","โรงพยาบาลพระรามเก้า","Praram 9 Hospital","Healthcare"],["STGT","ศรีตรังโกลฟส์","Sri Trang Gloves","Healthcare"],
 ["IVL","อินโดรามา เวนเจอร์ส","Indorama Ventures","Petrochem"],["VGI","วีจีไอ","VGI","Media"],["PLANB","แพลน บี มีเดีย","Plan B Media","Media"],
 ["MAJOR","เมเจอร์ ซีนีเพล็กซ์","Major Cineplex","Media"],["STA","ศรีตรังแอโกรอินดัสทรี","Sri Trang Agro","Agri"],["NER","นอร์ทอีส รับเบอร์","North East Rubber","Agri"],
 ["JMART","เจ มาร์ท","Jaymart","Commerce"],["SINGER","ซิงเกอร์ประเทศไทย","Singer Thailand","Commerce"],["M","เอ็มเค เรสโตรองต์","MK Restaurant","Food"],
 ["TLI","ไทยประกันชีวิต","Thai Life Insurance","Insurance"],["BLA","กรุงเทพประกันชีวิต","Bangkok Life Assurance","Insurance"],["THG","ธนบุรี เฮลท์แคร์","Thonburi Healthcare","Healthcare"],
 ["WHAUP","ดับบลิวเอชเอ ยูทิลิตี้ส์","WHA Utilities & Power","Utilities"],["TIPH","ทิพย กรุ๊ป","Dhipaya Group","Insurance"],["AURA","ออโรร่า ดีไซน์","Aurora Design","Commerce"]
];

// deterministic PRNG so the demo is stable across runs
function seed(str){let h=1779033703^str.length;for(let i=0;i<str.length;i++){h=Math.imul(h^str.charCodeAt(i),3432918353);h=h<<13|h>>>19;}return function(){h=Math.imul(h^h>>>16,2246822507);h=Math.imul(h^h>>>13,3266489909);return((h^=h>>>16)>>>0)/4294967296;};}
const R=(t,k)=>seed(t+k)();

// because is emitted as language-neutral codes ("momentum:pos") → rendered TH/EN in the page

const stocks = U.map(([tk,th,en,sec])=>{
  const f={value:R(tk,'v'),quality:R(tk,'q'),momentum:R(tk,'m'),growth:R(tk,'g'),health:R(tk,'h')};
  const score = +(0.28*f.quality+0.24*f.value+0.20*f.momentum+0.16*f.health+0.12*f.growth).toFixed(2);
  const verdict = score>=0.62?'BUY':score>=0.48?'WAIT':'AVOID';
  const risk_month_pct = -Math.round(8 + (1-f.health)*12 + (1-f.quality)*6 + R(tk,'r')*4);
  const max_weight = +Math.max(0.08, Math.min(0.40, 0.42*(1-Math.abs(risk_month_pct)/32))).toFixed(2);
  const p_win = +(0.44 + score*0.22).toFixed(2);
  const keys=Object.keys(f).sort((a,b)=>f[b]-f[a]);
  const top=keys[0], low=keys[keys.length-1];
  const because = verdict==='BUY' ? [top+':pos', keys[1]+':pos'] : [top+':pos', low+':neg'];
  const last = +(8 + R(tk,'p')*380).toFixed(2);
  const chg_pct = +((R(tk,'c')-0.5)*5).toFixed(1);
  return {ticker:tk+'.BK',name:en,name_th:th,sector:sec,score,verdict,risk_month_pct,max_weight,p_win,because,last,chg_pct};
}).sort((a,b)=>b.score-a.score);

const out={generated:"2026-07-31",universe:"SET100",disclaimer:"เพื่อการศึกษา ไม่ใช่คำแนะนำการลงทุน · ไม่รับประกันผลตอบแทน",stocks};
fs.writeFileSync("C:/Users/hzdjd/Downloads/atlas/setscout/today.json", JSON.stringify(out,null,0));
console.log("wrote",stocks.length,"stocks · BUY",stocks.filter(s=>s.verdict==='BUY').length,"WAIT",stocks.filter(s=>s.verdict==='WAIT').length,"AVOID",stocks.filter(s=>s.verdict==='AVOID').length);
