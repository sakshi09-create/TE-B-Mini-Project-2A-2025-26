import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
from sklearn.ensemble import RandomForestClassifier
import joblib

# Much more comprehensive and balanced dataset - Including Hindi and Marathi translations
data = {
    "message": [
        # FRAUD messages - Financial scams (English)
        "You have won $1000 lottery, click here to claim",
        "Update your bank details immediately or account blocked", 
        "Congratulations! You won a free vacation",
        "Free Msg-J.P. Morgan Chase Bank Alert-Did You Attempt A Zelle Payment For The Amount of $5000.00? Reply YES or NO Or 1 To Decline Fraud Alerts",
        "URGENT: Your account has been suspended. Click to verify immediately",
        "You've won $50000! Claim your prize now by calling this number",
        "Bank of America: Suspicious activity detected. Verify your account now",
        "PayPal: Your account will be limited. Update payment method immediately",
        "Amazon: Your order of $999 has been placed. Cancel if not you by clicking here",
        "IRS: You owe back taxes. Pay immediately to avoid arrest",
        "Your credit card has been charged $500. Dispute now by clicking link",
        "Chase Bank: Fraud alert on your account. Reply YES to confirm transaction",
        "Wells Fargo: Your account is locked. Click to unlock immediately",
        "Apple ID suspended due to security issues. Verify now or lose access",
        "Microsoft: Your computer is infected. Call tech support immediately",
        "You are pre-approved for $10000 loan. Apply now, limited time offer",
        "Government grant available. Claim your $5000 now before it expires",
        "Walmart gift card winner! Claim $500 card now by calling",
        "Your package is held at customs. Pay $5 shipping fee to release",
        "Final notice: Your subscription will be charged $99 unless you cancel",
        "Bitcoin investment opportunity! Double your money in 24 hours",
        "Nigerian prince needs help transferring millions. Share in profits",
        "Tax refund of $2500 waiting. Click to claim before deadline",
        "Your Social Security number has been suspended. Call immediately",
        "Free iPhone 15! You're our 1000th visitor. Claim now!",
        
        # FRAUD messages - Financial scams (Hindi)
        "आपने 1000 डॉलर का लॉटरी जीता है, दावा करने के लिए यहां क्लिक करें",
        "तुरंत अपना बैंक विवरण अपडेट करें या खाता अवरुद्ध हो जाएगा",
        "बधाई हो! आपको एक निःशुल्क छुट्टी मिली है",
        "मुफ्त संदेश-जे.पी. मॉर्गन चेस बैंक अलर्ट-क्या आपने 5000 डॉलर का ज़ेले भुगतान करने का प्रयास किया? हाँ या नहीं या 1 धोखाधड़ी चेतावनी को अस्वीकार करने के लिए",
        "तत्काल: आपका खाता निलंबित कर दिया गया है। तुरंत सत्यापित करने के लिए क्लिक करें",
        "आपने 50000 डॉलर जीते हैं! अब इस नंबर पर कॉल करके अपना पुरस्कार प्राप्त करें",
        "बैंक ऑफ अमेरिका: संदिग्ध गतिविधि का पता चला। अब अपने खाते को सत्यापित करें",
        "पेपैल: आपका खाता सीमित हो जाएगा। तुरंत भुगतान विधि अपडेट करें",
        "अमेज़ॅन: आपका 999 डॉलर का ऑर्डर दिया गया है। यहां क्लिक करके रद्द करें यदि आप नहीं हैं",
        "IRS: आपके पास बकाया कर है। गिरफ्तारी से बचने के लिए तुरंत भुगतान करें",
        "आपके क्रेडिट कार्ड से 500 डॉलर चार्ज किए गए हैं। लिंक पर क्लिक करके अब विवाद करें",
        "चेस बैंक: आपके खाते पर धोखाधड़ी चेतावनी। लेनदेन की पुष्टि के लिए हाँ का उत्तर दें",
        "वेल्स फार्गो: आपका खाता लॉक हो गया है। तुरंत अनलॉक करने के लिए क्लिक करें",
        "एप्पल आईडी सुरक्षा समस्याओं के कारण निलंबित। अब सत्यापित करें या पहुंच खो दें",
        "माइक्रोसॉफ्ट: आपका कंप्यूटर संक्रमित है। तुरंत तकनीकी सहायता कॉल करें",
        "आपके लिए 10000 डॉलर के ऋण के लिए पूर्व-अनुमोदन। अब आवेदन करें, सीमित समय की पेशकश",
        "सरकारी अनुदान उपलब्ध है। इसके समाप्त होने से पहले अपने 5000 डॉलर का दावा करें",
        "वॉलमार्ट गिफ्ट कार्ड विजेता! अब कॉल करके 500 डॉलर कार्ड का दावा करें",
        "आपका पैकेज कस्टम्स में रोका गया है। रिलीज़ करने के लिए 5 डॉलर की शिपिंग फीस का भुगतान करें",
        "अंतिम सूचना: आपकी सदस्यता से 99 डॉलर चार्ज किए जाएंगे जब तक आप रद्द नहीं करते",
        "बिटकॉइन निवेश अवसर! 24 घंटों में अपने पैसे को दोगुना करें",
        "नाइजीरियाई राजकुमार को दस मिलियन स्थानांतरित करने में मदद की आवश्यकता है। लाभ में शेयर करें",
        "2500 डॉलर की कर वापसी प्रतीक्षा में है। समय सीमा से पहले दावा करने के लिए क्लिक करें",
        "आपका सोशल सिक्योरिटी नंबर निलंबित कर दिया गया है। तुरंत कॉल करें",
        "मुफ्त आईफोन 15! आप हमारे 1000 वें आगंतुक हैं। अब दावा करें!",
        
        # FRAUD messages - Financial scams (Marathi)
        "तुम्ही 1000$ चे लॉटरी जिंकले आहे, दावा करण्यासाठी इथे क्लिक करा",
        "तातडीने तुमची बँक तपशील अद्ययावत करा किंवा खाते अवरोधित केले जाईल",
        "अभिनंदन! तुम्हाला एक मोफत सुटी मिळाली आहे",
        "मोफत संदेश-जे.पी. मॉर्गन चेस बँक अलर्ट-तुम्ही का 5000$ चे झेले देयक दिले? होय किंवा नाही किंवा 1 फ्रॉड अलर्ट नाकारण्यासाठी",
        "तातडीने: तुमचे खाते निलंबित केले गेले आहे. लगेच सत्यापित करण्यासाठी क्लिक करा",
        "तुम्ही 50000$ जिंकले आहेत! आता हा नंबर कॉल करून तुमचा बक्षीस मिळवा",
        "बँक ऑफ अमेरिका: संशयास्पद क्रियाकलाप आढळला. आता तुमचे खाते सत्यापित करा",
        "पेपअल: तुमचे खाते मर्यादित केले जाईल. लगेच देयक पद्धत अद्ययावत करा",
        "अमेझॉन: तुमचा 999$ चा ऑर्डर दिला गेला आहे. इथे क्लिक करून रद्द करा जर तुम्ही नसाल तर",
        "IRS: तुमच्याकडे बाकी कर आहे. अटकपटकापास टाळण्यासाठी लगेच भरा",
        "तुमच्या क्रेडिट कार्डवर 500$ चार्ज केले गेले आहेत. लिंकवर क्लिक करून आता वाद करा",
        "चेस बँक: तुमच्या खात्यावर फ्रॉड अलर्ट. व्यवहार पुष्टी करण्यासाठी होय उत्तर द्या",
        "वेल्स फार्गो: तुमचे खाते लॉक केले गेले आहे. लगेच अनलॉक करण्यासाठी क्लिक करा",
        "ॲप्पल आयडी सुरक्षा समस्यांमुळे निलंबित. आता सत्यापित करा किंवा प्रवेश गमावा",
        "मायक्रोसॉफ्ट: तुमचा संगणक संक्रमित आहे. लगेच तांत्रिक सहाय्य कॉल करा",
        "तुमच्यासाठी 10000$ च्या कर्जासाठी पूर्व-मंजूरी. आता अर्ज करा, मर्यादित कालावधी ऑफर",
        "शासन अनुदान उपलब्ध आहे. ते संपण्यापूर्वी तुमच्या 5000$ चा दावा करा",
        "वॉलमार्ट भेट कार्ड विजेता! आता कॉल करून 500$ कार्ड दावा करा",
        "तुमचा पॅकेज सीमा मध्ये रोखला गेला आहे. सोडवण्यासाठी 5$ शिपिंग फी भरा",
        "शेवटची सूचना: तुमच्या सदस्यतेवर 99$ चार्ज केले जातील जोपर्यंत तुम्ही रद्द करत नाही",
        "बिटकॉइन गुंतवणूक अवसर! 24 तासांत तुमचे पैसे दुप्पट करा",
        "नायजेरियन प्रिन्सला दस मिलियन हस्तांतरित करण्यास मदत हवी आहे. फायद्यात भाग घ्या",
        "2500$ ची कर परतावा वाट पाहत आहे. कालावधीपूर्वी दावा करण्यासाठी क्लिक करा",
        "तुमचा सोशल सिक्युरिटी क्रमांक निलंबित केला गेला आहे. लगेच कॉल करा",
        "मोफत आयफोन 15! तुम्ही आमचे 1000 वे अतिथी आहात. आता दावा करा!",
        
        # SAFE messages - Legitimate communications (English)
        "Meeting at 10 AM tomorrow, please join",
        "Your package will be delivered today between 2-4 PM",
        "Project deadline is extended to next week",
        "Happy birthday! Hope you have a great day",
        "Lunch is ready, come downstairs",
        "Can you pick up milk on your way home?",
        "The weather is nice today, perfect for a walk",
        "Don't forget about the dentist appointment at 3 PM",
        "Movie starts at 8 PM, see you there",
        "Thanks for helping me with the project",
        "Good morning! Have a great day at work",
        "The meeting has been moved to conference room B",
        "Your flight is scheduled to depart at 2:30 PM",
        "Reminder: Parent-teacher conference tomorrow",
        "The restaurant reservation is confirmed for 7 PM",
        "Your library books are due next week",
        "Traffic is heavy on main street, take alternate route",
        "The gym class is cancelled today",
        "Your prescription is ready for pickup at the pharmacy",
        "School is closed due to weather conditions",
        "Call me when you reach home",
        "Don't forget to water the plants",
        "The groceries have been delivered",
        "Your appointment is confirmed for Friday",
        "Please review the document and send feedback",
        
        # SAFE messages - Legitimate communications (Hindi)
        "कल 10 बजे मीटिंग है, कृपया शामिल हों",
        "आपका पैकेज आज 2-4 बजे के बीच डिलीवर किया जाएगा",
        "प्रोजेक्ट की समय सीमा अगले सप्ताह तक बढ़ा दी गई है",
        "जन्मदिन की बधाई! आशा है कि आपका दिन शानदार होगा",
        "लंच तैयार है, नीचे आइए",
        "क्या आप घर लौटते समय दूध ले सकते हैं?",
        "आज मौसम अच्छा है, टहलने के लिए उपयुक्त",
        "3 बजे दंत चिकित्सक के अपॉइंटमेंट के बारे में मत भूलना",
        "फिल्म 8 बजे शुरू होती है, वहां मिलते हैं",
        "प्रोजेक्ट में मेरी मदद करने के लिए धन्यवाद",
        "शुभ प्रभात! काम पर शानदार दिन बिताइए",
        "मीटिंग को कॉन्फ्रेंस रूम बी में स्थानांतरित कर दिया गया है",
        "आपकी उड़ान 2:30 बजे रवाना होने के लिए निर्धारित है",
        "अनुस्मारक: कल माता-पिता और शिक्षक की बैठक है",
        "रेस्तरां की बुकिंग 7 बजे के लिए पुष्टि हो गई है",
        "आपकी पुस्तकालय की पुस्तकें अगले सप्ताह वापस करनी हैं",
        "मुख्य सड़क पर यातायात भीड़ है, वैकल्पिक मार्ग लें",
        "आज जिम क्लास रद्द हो गया है",
        "आपकी दवा फार्मेसी में लेने के लिए तैयार है",
        "मौसम की स्थिति के कारण स्कूल बंद है",
        "घर पहुंचने पर मुझे कॉल करें",
        "पौधों को पानी देना न भूलें",
        "किराने का सामान डिलीवर हो गया है",
        "आपकी अपॉइंटमेंट शुक्रवार के लिए पुष्टि हो गई है",
        "कृपया दस्तावेज़ की समीक्षा करें और प्रतिक्रिया भेजें",
        
        # SAFE messages - Legitimate communications (Marathi)
        "उद्या सकाळी 10 वाजता बैठक आहे, कृपया सहभाग घ्या",
        "तुमचा पॅकेज आज 2-4 दरम्यान वितरित केला जाईल",
        "प्रकल्पाची मुदत पुढच्या आठवड्यापर्यंत वाढविली गेली आहे",
        "वाढदिवसाच्या हार्दिक शुभेच्छा! तुमचा दिवस छान जावो अशी आशा",
        "जेवण तयार आहे, खाली या",
        "तुमच्या मार्गात दूध आणू शकता का?",
        "आजचे हवामान छान आहे, फिरण्यासाठी योग्य",
        "3 वाजता दंत चिकित्सकाच्या अपॉइंटमेंटचे लक्षात ठेवू नका",
        "चित्रपट 8 वाजता सुरू होतो, तिथे भेटू",
        "प्रकल्पात माझी मदत केल्याबद्दल धन्यवाद",
        "शुभ प्रभात! कामात छान दिवस घालवा",
        "बैठकला कॉन्फ्रेंस रूम बी मध्ये हलविले गेले आहे",
        "तुमची विमाने 2:30 वाजता सुटण्याची नियोजित आहे",
        "स्मरणपत्र: उद्या माता-पिता आणि शिक्षक बैठक",
        "रेस्टॉरंट रिझर्वेशन 7 वाजता पुष्टी झाले आहे",
        "तुमची पुस्तकालयाची पुस्तके पुढच्या आठवड्यापर्यंत द्यावी लागतील",
        "मुख्य रस्त्यावर रहदारी जास्त आहे, पर्यायी मार्ग निवडा",
        "आज जिम वर्ग रद्द झाला आहे",
        "तुमची औषधे फार्मसी मध्ये घेण्यासाठी तयार आहेत",
        "हवामानामुळे शाळा बंद आहे",
        "घरी पोहोचल्यावर मला कॉल करा",
        "वनस्पतींना पाणी देणे विसरू नका",
        "किराणा घरी आला आहे",
        "तुमची अपॉइंटमेंट शुक्रवारी पुष्टी झाली आहे",
        "कृपया दस्तऐवजाचे अवलोकन करा आणि अभिप्राय पाठवा",
        
        # SAFE messages - Public service and educational (English)
        "Say no to drugs, and yes to life. Anti Narcotics Cell, Crime Branch, Thane City",
        "Wear your seatbelt for safety. Traffic Police Department",
        "Get vaccinated. Stay safe. Ministry of Health",
        "Report suspicious activity to local police immediately",
        "Fire safety tips: Check smoke detectors monthly",
        "Blood donation camp tomorrow at community center",
        "Environmental awareness: Reduce, reuse, recycle",
        "Vote for your future. Election Commission reminder",
        "Cyber safety: Never share personal information online",
        "Mental health matters. Seek help if needed",
        "Educational workshop on financial literacy next week",
        "Community cleanup drive this Saturday morning",
        "First aid training session registration open",
        "Senior citizen health checkup camp announced",
        "Youth employment program applications accepted",
        "Road safety week: Drive carefully, arrive safely",
        "Water conservation tips for summer season",
        "Digital India initiative: Learn computer skills",
        "Women safety helpline number: Call for help",
        "Child protection awareness: Report abuse cases",
        "Emergency contact: 100 for police, 101 for fire",
        "Noise pollution control: Keep volume low after 10 PM",
        "Public transport: Use buses to reduce traffic",
        "Waste management: Segregate waste at source",
        "Energy saving: Switch off lights when not in use",
        
        # SAFE messages - Public service and educational (Hindi)
        "नशों का ना कहें, और जीवन का हां कहें। एंटी नारकोटिक्स सेल, क्राइम ब्रांच, ठाणे शहर",
        "सुरक्षा के लिए अपना सीटबेल्ट बांधें। ट्रैफिक पुलिस विभाग",
        "टीका लगवाएं। सुरक्षित रहें। स्वास्थ्य मंत्रालय",
        "संदिग्ध गतिविधि की तुरंत स्थानीय पुलिस को रिपोर्ट करें",
        "अग्निशमन सुरक्षा युक्तियाँ: धूम्रपाती का निरीक्षण मासिक करें",
        "कल युवा केंद्र में रक्तदान शिविर",
        "पर्यावरण जागरूकता: कम करें, पुन: उपयोग करें, पुन: चक्रण करें",
        "अपने भविष्य के लिए वोट करें। चुनाव आयोग अनुस्मारक",
        "साइबर सुरक्षा: कभी भी ऑनलाइन व्यक्तिगत जानकारी साझा न करें",
        "मानसिक स्वास्थ्य महत्वपूर्ण है। आवश्यकता होने पर सहायता लें",
        "अगले सप्ताह वित्तीय साक्षरता पर शैक्षणिक कार्यशाला",
        "इस शनिवार सुबह सामुदायिक सफाई अभियान",
        "प्रथम सहायता प्रशिक्षण सत्र पंजीकरण खुला है",
        "वरिष्ठ नागरिक स्वास्थ्य जांच शिविर की घोषणा",
        "युवा रोजगार कार्यक्रम आवेदन स्वीकृत",
        "सड़क सुरक्षा सप्ताह: सावधानीपूर्वक ड्राइव करें, सुरक्षित रूप से पहुंचें",
        "ग्रीष्म ऋतु के लिए जल संरक्षण युक्तियाँ",
        "डिजिटल इंडिया पहल: कंप्यूटर कौशल सीखें",
        "महिला सुरक्षा हेल्पलाइन नंबर: सहायता के लिए कॉल करें",
        "बाल सुरक्षा जागरूकता: दुर्व्यवहार की रिपोर्ट करें",
        "आपातकालीन संपर्क: पुलिस के लिए 100, अग्निशमन के लिए 101",
        "शोर प्रदूषण नियंत्रण: रात 10 बजे के बाद आवाज कम रखें",
        "सार्वजनिक परिवहन: यातायात कम करने के लिए बसों का उपयोग करें",
        "कचरा प्रबंधन: स्रोत पर कचरा अलग करें",
        "ऊर्जा बचत: उपयोग न होने पर बिजली बंद करें",
        
        # SAFE messages - Public service and educational (Marathi)
        "नशा म्हणा नाही, आणि जीवन म्हणा होय. ॲन्टी नारकोटिक्स सेल, क्राइम ब्रांच, ठाणे शहर",
        "सुरक्षिततेसाठी सीटबेल्ट घाला. ट्राफिक पोलिस विभाग",
        "लसीकरण करा. सुरक्षित रहा. आरोग्य मंत्रालय",
        "संशयास्पद क्रियाकलापाची लगेच स्थानिक पोलिसला अहवाल द्या",
        "अग्निशमन सुरक्षा टिपा: धूम्रपातीची मासिक तपासणी करा",
        "उद्या समुदाय केंद्रात रक्तदान शिबिर",
        "पर्यावरण जागरूकता: कमी करा, पुन्हा वापरा, पुन्हा चक्रावर्तन करा",
        "तुमच्या भविष्यासाठी मतदान करा. निवडणूक आयोग स्मरणपत्र",
        "सायबर सुरक्षा: कधीही ऑनलाइन वैयक्तिक माहिती सामायिक करू नका",
        "मानसिक आरोग्य महत्त्वाचे आहे. आवश्यकता असल्यास मदत घ्या",
        "पुढच्या आठवड्यात वित्तीय साक्षरतेवर शैक्षणिक कार्यशाळा",
        "या शनिवारी सकाळी समुदाय स्वच्छता अभियान",
        "प्राथमिक उपचार प्रशिक्षण सत्र नोंदणी उघडे आहे",
        "वयोवृद्ध नागरिक आरोग्य तपास शिबिर घोषित",
        "युवा रोजगार कार्यक्रम अर्ज स्वीकारले",
        "रस्ता सुरक्षा आठवडा: काळजीपूर्वक ड्राइव्ह करा, सुरक्षितपणे पोहोचा",
        "उन्हाळ्यासाठी पाणी संरक्षण टिपा",
        "डिजिटल इंडिया उपक्रम: संगणक कौशल्य शिका",
        "महिला सुरक्षा हेल्पलाइन क्रमांक: मदतीसाठी कॉल करा",
        "मुलांच्या सुरक्षेची जागरूकता: दुर्व्यवहाराची अहवाल द्या",
        "आपत्कालीन संपर्क: पोलिससाठी 100, अग्निशमनासाठी 101",
        "आवाज प्रदूषण नियंत्रण: रात्री 10 वाजल्यानंतर आवाज कमी ठेवा",
        "सार्वजनिक वाहतूक: रस्ता ओझे कमी करण्यासाठी बस वापरा",
        "कचरा व्यवस्थापन: स्त्रोतावर कचरा वेगळा करा",
        "ऊर्जा बचत: वापर नसताना लाइट बंद करा",
        
        # SAFE messages - Business and notifications (English)
        "Your appointment with Dr. Smith is confirmed for Monday",
        "Grocery store sale: 20% off fresh produce this week",
        "Library closed for maintenance on Sunday",
        "New bus route starting from downtown to airport",
        "Community center yoga classes begin next month",
        "Local farmers market open every Saturday morning",
        "Power outage scheduled for maintenance tomorrow 2-4 PM",
        "Water supply will be interrupted for repairs",
        "Road construction on Main Street, expect delays",
        "New parking regulations effective from next month",
        "Store hours extended until 10 PM this week",
        "New restaurant opening this Friday",
        "Online portal maintenance this weekend",
        "Mobile app update available now",
        "Special discount for returning customers",
        "New product launch next week",
        "Seasonal sale starting Monday",
        "Customer feedback survey - please participate",
        "New branch opening downtown",
        "Service upgrade scheduled for Tuesday",
        "Holiday closure: Office closed Dec 25",
        "New payment options now available",
        "Loyalty program points doubled this month",
        "Free Wi-Fi now available in store",
        "New loyalty card available at checkout",
        
        # SAFE messages - Business and notifications (Hindi)
        "डॉ. स्मिथ के साथ आपकी अपॉइंटमेंट सोमवार के लिए पुष्टि हो गई है",
        "किराना स्टोर सेल: इस सप्ताह ताजा उत्पादों पर 20% छूट",
        "रविवार को रखरखाव के लिए पुस्तकालय बंद है",
        "शहर के केंद्र से हवाई अड्डे तक नया बस मार्ग शुरू",
        "अगले महीने से सामुदायिक केंद्र में योगा क्लास शुरू",
        "स्थानीय किसान बाजार हर शनिवार सुबह खुला है",
        "कल 2-4 बजे रखरखाव के लिए बिजली कटौती निर्धारित है",
        "मरम्मत के लिए पानी की आपूर्ति में बाधा आएगी",
        "मुख्य सड़क पर सड़क निर्माण, देरी की अपेक्षा करें",
        "अगले महीने से नए पार्किंग नियम प्रभावी",
        "इस सप्ताह स्टोर के घंटे रात 10 बजे तक बढ़ाए गए",
        "इस शुक्रवार को नया रेस्तरां खुल रहा है",
        "इस सप्ताहांत ऑनलाइन पोर्टल रखरखाव",
        "मोबाइल ऐप अपडेट अब उपलब्ध",
        "लौटने वाले ग्राहकों के लिए विशेष छूट",
        "अगले सप्ताह नए उत्पाद की शुरुआत",
        "सोमवार से शुरू हो रही सीजनल सेल",
        "ग्राहक प्रतिक्रिया सर्वे - कृपया भाग लें",
        "शहर केंद्र में नई शाखा खुल रही है",
        "मंगलवार को सेवा अपग्रेड निर्धारित",
        "छुट्टी: कार्यालय 25 दिसंबर को बंद रहेगा",
        "नए भुगतान विकल्प अब उपलब्ध",
        "इस महीने लॉयल्टी प्रोग्राम अंक दोगुने",
        "स्टोर में अब मुफ्त वाई-फाई उपलब्ध",
        "चेकआउट पर नया लॉयल्टी कार्ड उपलब्ध",
        
        # SAFE messages - Business and notifications (Marathi)
        "डॉ. स्मिथ यांच्यासह तुमची अपॉइंटमेंट सोमवारी पुष्टी झाली आहे",
        "किराणा दुकान विक्री: या आठवड्यात ताजे उत्पादनांवर 20% सूट",
        "रविवारी देखभालीसाठी ग्रंथालय बंद आहे",
        "शहराच्या केंद्रापासून विमानतळापर्यंत नवीन बस मार्ग सुरू",
        "पुढच्या महिन्यापासून समुदाय केंद्रात योगा वर्ग सुरू होतील",
        "स्थानिक शेतकऱ्यांचे बाजार प्रत्येक शनिवारी सकाळी उघडे आहे",
        "उद्या 2-4 वाजता देखभालीसाठी वीज पुरवठा नियोजित आहे",
        "दुरुस्तीसाठी पाणीपुरवठा अडथळा येईल",
        "मुख्य रस्त्यावर रस्ता बांधकाम, विलंबाची अपेक्षा करा",
        "पुढच्या महिन्यापासून नवीन पार्किंग नियम प्रभावी होतील",
        "या आठवड्यात स्टोअर तास रात्री 10 वाजता पर्यंत वाढविले",
        "या शुक्रवारी नवीन रेस्टॉरंट उघडणार",
        "या आठवड्यांत ऑनलाइन पोर्टल देखभाल",
        "मोबाइल अॅप अपडेट आता उपलब्ध",
        "परत येणाऱ्या ग्राहकांसाठी विशेष सूट",
        "पुढच्या आठवड्यात नवीन उत्पादन प्रक्षेपण",
        "सोमवारी सुरू होणारी हंगामी विक्री",
        "ग्राहक प्रतिसाद सर्वे - कृपया सहभाग घ्या",
        "शहर केंद्रात नवीन शाखा उघडणार",
        "मंगळवारी सेवा सुधारणा नियोजित",
        "सुट्टी: कार्यालय 25 डिसेंबर रोजी बंद असेल",
        "नवीन देयक पर्याय आता उपलब्ध",
        "या महिन्यात निष्ठावंतता कार्यक्रम गुण दुप्पट",
        "स्टोअर मध्ये आता मोफत वाय-फाय उपलब्ध",
        "चेकआऊट वर नवीन निष्ठावंतता कार्ड उपलब्ध"
    ],
    "label": [
        # Fraud labels (25 messages in English)
        "fraud", "fraud", "fraud", "fraud", "fraud", "fraud", "fraud", 
        "fraud", "fraud", "fraud", "fraud", "fraud", "fraud", "fraud",
        "fraud", "fraud", "fraud", "fraud", "fraud", "fraud", "fraud",
        "fraud", "fraud", "fraud", "fraud",
        
        # Fraud labels (25 messages in Hindi)
        "fraud", "fraud", "fraud", "fraud", "fraud", "fraud", "fraud", 
        "fraud", "fraud", "fraud", "fraud", "fraud", "fraud", "fraud",
        "fraud", "fraud", "fraud", "fraud", "fraud", "fraud", "fraud",
        "fraud", "fraud", "fraud", "fraud",
        
        # Fraud labels (25 messages in Marathi)
        "fraud", "fraud", "fraud", "fraud", "fraud", "fraud", "fraud", 
        "fraud", "fraud", "fraud", "fraud", "fraud", "fraud", "fraud",
        "fraud", "fraud", "fraud", "fraud", "fraud", "fraud", "fraud",
        "fraud", "fraud", "fraud", "fraud",
        
        # Safe labels (25 messages in English - Personal)
        "safe", "safe", "safe", "safe", "safe", "safe", "safe",
        "safe", "safe", "safe", "safe", "safe", "safe", "safe", 
        "safe", "safe", "safe", "safe", "safe", "safe", "safe",
        "safe", "safe", "safe", "safe",
        
        # Safe labels (25 messages in Hindi - Personal)
        "safe", "safe", "safe", "safe", "safe", "safe", "safe",
        "safe", "safe", "safe", "safe", "safe", "safe", "safe", 
        "safe", "safe", "safe", "safe", "safe", "safe", "safe",
        "safe", "safe", "safe", "safe",
        
        # Safe labels (25 messages in Marathi - Personal)
        "safe", "safe", "safe", "safe", "safe", "safe", "safe",
        "safe", "safe", "safe", "safe", "safe", "safe", "safe", 
        "safe", "safe", "safe", "safe", "safe", "safe", "safe",
        "safe", "safe", "safe", "safe",
        
        # Safe labels (25 messages in English - Public service)
        "safe", "safe", "safe", "safe", "safe", "safe", "safe",
        "safe", "safe", "safe", "safe", "safe", "safe", "safe", 
        "safe", "safe", "safe", "safe", "safe", "safe", "safe",
        "safe", "safe", "safe", "safe",
        
        # Safe labels (25 messages in Hindi - Public service)
        "safe", "safe", "safe", "safe", "safe", "safe", "safe",
        "safe", "safe", "safe", "safe", "safe", "safe", "safe", 
        "safe", "safe", "safe", "safe", "safe", "safe", "safe",
        "safe", "safe", "safe", "safe",
        
        # Safe labels (25 messages in Marathi - Public service)
        "safe", "safe", "safe", "safe", "safe", "safe", "safe",
        "safe", "safe", "safe", "safe", "safe", "safe", "safe", 
        "safe", "safe", "safe", "safe", "safe", "safe", "safe",
        "safe", "safe", "safe", "safe",
        
        # Safe labels (25 messages in English - Business)
        "safe", "safe", "safe", "safe", "safe", "safe", "safe",
        "safe", "safe", "safe", "safe", "safe", "safe", "safe", 
        "safe", "safe", "safe", "safe", "safe", "safe", "safe",
        "safe", "safe", "safe", "safe",
        
        # Safe labels (25 messages in Hindi - Business)
        "safe", "safe", "safe", "safe", "safe", "safe", "safe",
        "safe", "safe", "safe", "safe", "safe", "safe", "safe", 
        "safe", "safe", "safe", "safe", "safe", "safe", "safe",
        "safe", "safe", "safe", "safe",
        
        # Safe labels (25 messages in Marathi - Business)
        "safe", "safe", "safe", "safe", "safe", "safe", "safe",
        "safe", "safe", "safe", "safe", "safe", "safe", "safe", 
        "safe", "safe", "safe", "safe", "safe", "safe", "safe",
        "safe", "safe", "safe", "safe"
    ]
}

df = pd.DataFrame(data)
print(f"Dataset size: {len(df)} messages")
print(f"Fraud messages: {len(df[df['label'] == 'fraud'])}")
print(f"Safe messages: {len(df[df['label'] == 'safe'])}")

# Train model with better parameters and Random Forest for better accuracy
X_train, X_test, y_train, y_test = train_test_split(
    df["message"], df["label"], 
    test_size=0.2, 
    random_state=42, 
    stratify=df["label"]
)

# Use Random Forest instead of Naive Bayes for better performance
model = make_pipeline(
    TfidfVectorizer(
        lowercase=True,
        stop_words='english',
        ngram_range=(1, 3),  # Include trigrams
        min_df=1,
        max_df=0.9,
        max_features=1000
    ), 
    RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        class_weight='balanced'  # Handle class imbalance
    )
)

model.fit(X_train, y_train)

# Test the model
accuracy = model.score(X_test, y_test)
print(f"Model trained. Accuracy: {accuracy:.2%}")

# Test with specific messages in different languages
test_messages = [
    "Say no to drugs, and yes to life. Anti Narcotics Cell, Crime Branch, Thane City",
    "Free Msg-J.P. Morgan Chase Bank Alert-Did You Attempt A Zelle Payment For The Amount of $5000.00? Reply YES or NO",
    "Meeting at 10 AM tomorrow",
    "You won $1000 lottery! Click here to claim",
    "आपने 1000 डॉलर का लॉटरी जीता है, दावा करने के लिए यहां क्लिक करें",
    "कल 10 बजे मीटिंग है, कृपया शामिल हों",
    "तुम्ही 1000$ चे लॉटरी जिंकले आहे, दावा करण्यासाठी इथे क्लिक करा",
    "उद्या सकाळी 10 वाजता बैठक आहे, कृपया सहभाग घ्या"
]

print("\n--- Testing Messages ---")
for msg in test_messages:
    prediction = model.predict([msg])[0]
    confidence = max(model.predict_proba([msg])[0])
    print(f"Message: {msg[:50]}...")
    print(f"Prediction: {prediction} (Confidence: {confidence:.1%})")
    print()

# Save model
joblib.dump(model, "fraud_detector.pkl")
print("✅ Enhanced model saved as fraud_detector.pkl")