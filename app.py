"""Complete Enhanced Arabic Diacritizer"""

import gradio as gr
import pyarabic.araby as araby
import re
import datetime
import os
from typing import Dict, List, Tuple, Optional

class ArabicDiacritizer:
    def __init__(self):
        self.author = "تطوير وتحسين: حُسام فَضْل قَدُّور"
        
        # القواعد النحوية
        self.grammar_rules = {
            'ال': {
                'default': 'الْ',
                'sun_letters': 'ال'
            },
            'prepositions': {
                'في': 'فِي',
                'من': 'مِنْ',
                'إلى': 'إِلَى',
                'على': 'عَلَى',
                'عن': 'عَنْ',
                'ب': 'بِ',
                'ل': 'لِ',
                'ك': 'كَ',
                'حتى': 'حَتَّى',
                'منذ': 'مُنْذُ',
                'مذ': 'مُذْ'
            },
            'sun_letters': 'تثدذرزسشصضطظلن',
            'special_words': {
                'الله': 'اللَّهِ',
                'القرآن': 'الْقُرْآنِ',
                'النبي': 'النَّبِيِّ',
                'الإسلام': 'الْإِسْلَامِ',
                'محمد': 'مُحَمَّدٍ',
                'رب': 'رَبِّ',
                'الرحمن': 'الرَّحْمَنِ',
                'الرحيم': 'الرَّحِيمِ'
            },
            'five_nouns': {
                'أب': {'رفع': 'أَبُو', 'نصب': 'أَبَا', 'جر': 'أَبِي'},
                'أخ': {'رفع': 'أَخُو', 'نصب': 'أَخَا', 'جر': 'أَخِي'},
                'حم': {'رفع': 'حَمُو', 'نصب': 'حَمَا', 'جر': 'حَمِي'},
                'فم': {'رفع': 'فُو', 'نصب': 'فَا', 'جر': 'فِي'},
                'ذو': {'رفع': 'ذُو', 'نصب': 'ذَا', 'جر': 'ذِي'}
            }
        }
        
         # النواسخ
        self.connectors = {
            'كان': {'اسم': 'رفع', 'خبر': 'نصب', 'tashkeel': 'كَانَ'},
            'إن': {'اسم': 'نصب', 'خبر': 'رفع'},
            'أن': {'اسم': 'نصب', 'خبر': 'رفع'},
            'لكن': {'اسم': 'نصب', 'خبر': 'رفع'},
            'ليت': {'اسم': 'نصب', 'خبر': 'رفع'},
            'لعل': {'اسم': 'نصب', 'خبر': 'رفع'}
        }

        # قواعد التنوين
        self.tanween_rules = {
            'رفع': {
                'default': 'ٌ',
                'ة': 'ةٌ',
                'ا': 'اءٌ'
            },
            'نصب': {
                'default': 'ً',
                'ة': 'ةً',
                'ا': 'اءً'
            },
            'جر': {
                'default': 'ٍ',
                'ة': 'ةٍ',
                'ا': 'اءٍ'
            }
        }

        # قواعد الإعراب
        self.case_rules = {
            'رفع': {
                'default': 'ُ',
                'جمع_مذكر_سالم': 'ونَ',
                'مثنى': 'انِ'
            },
            'نصب': {
                'default': 'َ',
                'جمع_مذكر_سالم': 'ينَ',
                'مثنى': 'ينِ'
            },
            'جر': {
                'default': 'ِ',
                'جمع_مذكر_سالم': 'ينَ',
                'مثنى': 'ينِ'
            }
        }

        # قواعد الضمائر المتصلة
        self.pronouns = {
            'ه': {'default': 'هُ', 'جر': 'هِ'},
            'ها': 'هَا',
            'هم': 'هُمْ',
            'هن': 'هُنَّ',
            'ك': 'كَ',
            'كم': 'كُمْ',
            'كن': 'كُنَّ',
            'ي': 'ي'
        }

        # قواعد الأفعال
        self.verb_rules = {
            'ماضي': {
                'default': 'َ',
                'متصل': 'ْ'
            },
            'مضارع': {
                'مرفوع': 'ُ',
                'منصوب': 'َ',
                'مجزوم': 'ْ'
            }
        }

    def apply_sun_letters_rule(self, word):
        """معالجة ال التعريف مع الحروف الشمسية"""
        if len(word) > 2 and word.startswith('ال'):
            if word[2] in self.grammar_rules['sun_letters']:
                return 'الْ' + word[2] + 'ّ' + word[3:]
        return word

    def apply_verb_rules(self, word: str, case: str) -> str:
        """تطبيق قواعد تشكيل الأفعال"""
        word = araby.strip_tashkeel(word)
        mudare_letters = 'أنيت'
        
        if word[0] in mudare_letters:  # فعل مضارع
            first_letter = 'يُ' if word[0] == 'ي' else word[0] + 'َ'
            rest_of_word = word[1:]
            
            if case == 'مرفوع':
                return first_letter + rest_of_word + self.verb_rules['مضارع']['مرفوع']
            elif case == 'منصوب':
                return first_letter + rest_of_word + self.verb_rules['مضارع']['منصوب']
            elif case == 'مجزوم':
                return first_letter + rest_of_word + self.verb_rules['مضارع']['مجزوم']
        else:  # فعل ماضي
            if word.endswith(('ت', 'نا', 'تم', 'تن', 'تما')):
                return word[:-len(word.split()[-1])] + 'ْ' + word.split()[-1]
            else:
                return word + self.verb_rules['ماضي']['default']
        
        return word

    def apply_five_noun_rules(self, word: str, case: str) -> str:
        """تطبيق قواعد الأسماء الخمسة"""
        for noun in self.grammar_rules['five_nouns']:
            if word.startswith(noun):
                return self.grammar_rules['five_nouns'][noun][case]
        return word

    def apply_tanween(self, word: str, case: str) -> str:
        """تطبيق قواعد التنوين"""
        if word.endswith('ة'):
            return word[:-1] + self.tanween_rules[case]['ة']
        elif word.endswith('ا'):
            return word[:-1] + self.tanween_rules[case]['ا']
        else:
            return word + self.tanween_rules[case]['default']

    def apply_case_mark(self, word: str, case: str, word_type: str) -> str:
        """تطبيق علامات الإعراب"""
        if word_type == 'جمع_مذكر_سالم':
            return word[:-2] + self.case_rules[case]['جمع_مذكر_سالم']
        elif word_type == 'مثنى':
            return word[:-2] + self.case_rules[case]['مثنى']
        else:
            return word + self.case_rules[case]['default']

    def apply_pronoun_rules(self, word: str, case: str) -> str:
        """تطبيق قواعد الضمائر المتصلة"""
        for pronoun, diacritic in self.pronouns.items():
            if word.endswith(pronoun):
                if isinstance(diacritic, dict):
                    pronoun_mark = diacritic.get(case, diacritic['default'])
                else:
                    pronoun_mark = diacritic
                return word[:-len(pronoun)] + pronoun_mark
        return word

    def detect_word_context(self, word: str, previous_word: Optional[str], next_word: Optional[str]) -> Dict[str, str]:
        """تحديد سياق الكلمة في الجملة"""
        context = {
            'type': 'unknown',
            'case': 'default',
            'has_tanween': False,
            'has_pronoun': False
        }

        if previous_word in self.grammar_rules['prepositions']:
            context['type'] = 'مجرور'
            context['case'] = 'جر'
        elif previous_word in self.connectors:
            connector_rules = self.connectors[previous_word]
            context['type'] = 'اسم_ناسخ'
            context['case'] = connector_rules['اسم']
        elif self.is_verb(word):
            context['type'] = 'فعل'
            context['case'] = self.detect_verb_case(word)
        elif self.is_five_noun(word):
            context['type'] = 'اسم_خمسة'
        
        if self.should_have_tanween(word, context['type']):
            context['has_tanween'] = True
        
        if self.has_attached_pronoun(word):
            context['has_pronoun'] = True
        
        return context

    def is_verb(self, word: str) -> bool:
        """التحقق مما إذا كانت الكلمة فعلاً"""
        mudare_letters = 'أنيت'
        if word[0] in mudare_letters:
            return True
        past_endings = ['', 'ت', 'نا', 'وا', 'تم', 'تن']
        return any(word.endswith(end) for end in past_endings)

    def detect_verb_case(self, word: str) -> str:
        """تحديد حالة الفعل"""
        if word[0] in 'أنيت':
            return 'مرفوع'
        return 'ماضي'

    def is_five_noun(self, word: str) -> bool:
        """التحقق من الأسماء الخمسة"""
        return any(word.startswith(noun) for noun in self.grammar_rules['five_nouns'])

    def should_have_tanween(self, word: str, word_type: str) -> bool:
        """تحديد التنوين"""
        if word_type in ['مجرور', 'اسم_ناسخ'] and not word.startswith('ال'):
            return True
        return False

    def has_attached_pronoun(self, word: str) -> bool:
        """التحقق من الضمائر المتصلة"""
        return any(word.endswith(pronoun) for pronoun in self.pronouns)

    def process_text(self, text: str) -> str:
        """معالجة النص الكامل"""
        if not text:
            return "الرجاء إدخال نص"

        try:
            sentences = re.split('[.!؟،]', text)
            processed_sentences = []

            for sentence in sentences:
                if not sentence.strip():
                    continue

                words = sentence.strip().split()
                processed_words = []

                for i, word in enumerate(words):
                    previous_word = words[i-1] if i > 0 else None
                    next_word = words[i+1] if i < len(words)-1 else None
                    
                    context = self.detect_word_context(word, previous_word, next_word)
                    processed_word = self.apply_diacritics(word, context)
                    processed_words.append(processed_word)

                processed_sentences.append(' '.join(processed_words))

            result = '. '.join(processed_sentences)
            self.save_text(result)
            return result

        except Exception as e:
            return f"حدث خطأ: {str(e)}"

    def apply_diacritics(self, word: str, context: Dict[str, str]) -> str:
        """تطبيق التشكيل على الكلمة"""
        word = araby.strip_tashkeel(word)
        
        if word in self.grammar_rules['special_words']:
            return self.grammar_rules['special_words'][word]
        
        if word.startswith('ال'):
            word = self.apply_sun_letters_rule(word)
        
        if context['type'] == 'اسم_خمسة':
            return self.apply_five_noun_rules(word, context['case'])
        
        if context['type'] == 'فعل':
            return self.apply_verb_rules(word, context['case'])
        
        if context['has_tanween']:
            word = self.apply_tanween(word, context['case'])
        else:
            word = self.apply_case_mark(word, context['case'], context['type'])
        
        if context['has_pronoun']:
            word = self.apply_pronoun_rules(word, context['case'])
        
        return word

    def save_text(self, text: str) -> None:
        """حفظ النص في ملف"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"diacritized_text_{timestamp}.txt"
        
        if not os.path.exists('outputs'):
            os.makedirs('outputs')
            
        filepath = os.path.join('outputs', filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"""
    {text}

    {'='*50}
    تم التشكيل بواسطة برنامج التشكيل العربي المتقدم
    {self.author}
    تاريخ التشكيل: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    خصائص التشكيل المطبقة:
    - معالجة الأسماء الخمسة
    - معالجة الحروف الشمسية والقمرية
    - تطبيق قواعد الإعراب الأساسية والمتقدمة
    - معالجة التنوين بأنواعه
    - معالجة الضمائر المتصلة
    - معالجة الأفعال وأزمنتها
    - معالجة النواسخ وأدوات الربط
    {'='*50}
    """)

def create_interface():
    diacritizer = ArabicDiacritizer()
    
    css = """
    footer {display: none !important}
    .gradio-footer {display: none !important}
    .api-docs {display: none !important}
    #api-info {display: none !important}
    .footer-links {display: none !important}
    """
    
    interface = gr.Interface(
        fn=diacritizer.process_text,
        inputs=gr.Textbox(
            label="أدخل النص العربي",
            placeholder="اكتب النص هنا...",
            lines=10
        ),
        outputs=gr.Textbox(
            label="النص مع التشكيل",
            lines=10
        ),
        title="برنامج التشكيل العربي المتقدم - النسخة المحسنة-5 ",
        description=f"""
        {diacritizer.author}
        برنامج متخصص في تشكيل النصوص العربية مع مراعاة:
        - القواعد النحوية الأساسية والمتقدمة
        - معالجة الأسماء الخمسة والأفعال
        - التنوين الصحيح بجميع أنواعه
        - معالجة الحروف الشمسية والقمرية
        - حالات الإعراب المختلفة
        - الضمائر المتصلة
        - النواسخ وأدوات الربط
        """,

        examples=[
            ["إنَّ إسحاقَ عليهِ السَّلامُ نبيٌّ مِنَ الأنبياءِ الكِرامِ"],
            ["في القرآنِ الكريمِ ذُكِرَ اسمُ إسحاقَ في مواضعَ عديدةٍ"],
            ["كانَ إسحاقُ عليهِ السَّلامُ مثالًا للصَّبرِ والحكمةِ"],
            ["جاء أبو محمدٍ إلى المسجدِ"],
            ["رأيت ذا العلمِ في المكتبةِ"]
        ],
        css=css
    )
    
    return interface

if __name__ == "__main__":
    demo = create_interface()
    demo.launch(server_name="127.0.0.1", 
               server_port=7865, 
               share=False,
               show_api=False,
               show_error=False)