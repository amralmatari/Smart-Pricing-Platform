import streamlit as st
import pandas as pd
import plotly.express as px
import io

# إعدادات الصفحة لتناسب اللغة العربية (RTL)
st.set_page_config(page_title="نظام تسعير منتجات الإضاءة", layout="wide")

# استايل بسيط لتحسين المظهر ودعم كامل للغة العربية
st.markdown("""
    <style>
    .stApp { direction: rtl; }
    h1, h2, h3, h4, h5, h6, p { text-align: right !important; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    .main { text-align: right; }
    div[data-testid="stSidebar"] { direction: rtl; text-align: right; }
    div[data-testid="stDataFrame"] { direction: rtl; text-align: right; }
    div[data-testid="stDialog"] { direction: rtl; text-align: right; }
    div[data-testid="stDialog"] .stMarkdown { text-align: right; }
    div.stButton > button { width: 100%; border-radius: 5px; height: 3em; background-color: #007bff; color: white; }
    footer {visibility: hidden;}
    .block-container {padding-bottom: 1rem !important;}
    
    /* تحسين شريط التمرير (Scrollbar) لتسهيل التحكم في الجداول على الجوال */
    ::-webkit-scrollbar { height: 8px; width: 8px; }
    ::-webkit-scrollbar-track { background: #f1f1f1; border-radius: 4px; }
    ::-webkit-scrollbar-thumb { background: #007bff; border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: #0056b3; }
    </style>
    """, unsafe_allow_html=True)

# هيدر التطبيق المخصص
st.markdown("""
    <div style="background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); padding: 15px 20px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); margin-bottom: 20px; text-align: center; color: white;">
        <h1 style="margin: 0; font-size: 26px; font-weight: bold; color: white; text-shadow: 1px 1px 2px rgba(0,0,0,0.3); text-align: center !important;">💡 منصة تسعير المنتجات الذكية</h1>
        <p style="margin: 5px 0 0 0; font-size: 15px; color: #e0e0e0; font-weight: 500; text-align: center !important;">المحلل التنافسي المتقدم للأسعار وهوامش الربح</p>
    </div>
""", unsafe_allow_html=True)

# القسم الأول: إدخال البيانات
st.markdown("### ⚙️ إعدادات النظام وإدخال البيانات")
tab_data, tab_settings = st.tabs(["📁 البيانات", "⚙️ التسعير"])

with tab_data:
    uploaded_file = st.file_uploader("ارفع ملف أسعار المنافسين (Excel or CSV)", type=['xlsx', 'csv'])
    
    st.markdown("---")
    st.markdown("**هل تحتاج إلى مساعدة في تنسيق الملف؟**")
    template_df = pd.DataFrame({
        "المنتج": ["مصباح LED 10W", "ثريا كريستال 50cm"], 
        "التكلفة": [15.0, 120.0], 
        "منافس 1": [20.0, 150.0], 
        "منافس 2": [22.0, 145.0],
        "منافس 3": [19.0, 160.0]
    })
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        template_df.to_excel(writer, index=False)
    st.download_button(
        "📥 تنزيل القالب المرجعي (Excel)",
        data=output.getvalue(),
        file_name="قالب_نظام_التسعير.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

    if uploaded_file and not st.session_state.get('tab_switched'):
        st.session_state.tab_switched = True
        st.components.v1.html("""<script>window.parent.document.querySelectorAll('button[data-baseweb="tab"]')[1].click();</script>""", height=0, width=0)
    
with tab_settings:
    target_discount = st.number_input("نسبة التخفيض عن متوسط السوق للانتشار (%)", min_value=0, max_value=100, value=10, step=1)
    min_profit_margin = st.number_input("الحد الأدنى لهامش الربح (%)", min_value=0, max_value=100, value=15, step=1)
    additional_expenses_pct = st.number_input("نسبة مصاريف إضافية على التكلفة (عمولات، شحن...) (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.5)
    decimals = st.number_input("عدد الخانات العشرية للتقريب", min_value=0, max_value=4, value=2, step=1)
if uploaded_file:
    # قراءة البيانات (نفترض وجود أعمدة: المنتج، التكلفة، سعر_المنافس_1، سعر_المنافس_2...)
    df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('xlsx') else pd.read_csv(uploaded_file)

    # تنظيف أسماء الأعمدة من المسافات الزائدة لتجنب مشاكل التسمية
    df.columns = df.columns.astype(str).str.strip()

    st.subheader("⚙️ تعيين الأعمدة (Column Mapping)")
    col1, col2 = st.columns(2)

    # محاولة تخمين الأعمدة الافتراضية
    def_prod = next((c for c in df.columns if 'منتج' in c or 'صنف' in c or 'Item' in c), df.columns[0])
    def_cost = next((c for c in df.columns if 'تكلفة' in c or 'Cost' in c), df.columns[1] if len(df.columns)>1 else df.columns[0])

    with col1:
        product_col_original = st.selectbox("اختر عمود اسم/كود المنتج:", df.columns, index=list(df.columns).index(def_prod))
    with col2:
        cost_col_original = st.selectbox("اختر عمود التكلفة:", df.columns, index=list(df.columns).index(def_cost))
    
    # إعادة تسمية الأعمدة المحددة إلى أسماء قياسية يستخدمها الكود
    # نحتفظ بنسخة من الأسماء الأصلية لكي لا يحدث تضارب
    if product_col_original != 'المنتج':
        df.rename(columns={product_col_original: 'المنتج'}, inplace=True)
    if cost_col_original != 'التكلفة' and cost_col_original != 'المنتج':
        df.rename(columns={cost_col_original: 'التكلفة'}, inplace=True)
    
    required_columns = ['المنتج', 'التكلفة']

    # تحديد أعمدة المنافسين بشكل ديناميكي (يمكن للمستخدم اختيارها)
    # استبعاد الأعمدة الأساسية وتحديد الأعمدة الرقمية فقط
    possible_competitors = [col for col in df.columns if col not in required_columns and pd.api.types.is_numeric_dtype(df[col])]

    st.subheader("⚙️ تحديد المنافسين")
    competitor_cols = st.multiselect("اختر أعمدة أسعار المنافسين من القائمة:", possible_competitors, default=possible_competitors)

    if not competitor_cols:
        st.warning("يرجى اختيار عمود واحد على الأقل للمنافسين لحساب متوسط السوق.")
        st.stop()

    # حساب المتوسط والحد الأدنى لأسعار المنافسين لكل صنف
    df['متوسط السوق'] = df[competitor_cols].mean(axis=1)
    df['أقل سعر سوق'] = df[competitor_cols].min(axis=1)

    # --- حساب التكلفة الشاملة ---
    df['التكلفة الشاملة'] = df['التكلفة'] * (1 + additional_expenses_pct/100)

    # 1. حساب هامش ربح السوق لكل منتج (كنسبة مضافة على التكلفة Markup)
    df['هامش ربح السوق (%)'] = ((df['متوسط السوق'] - df['التكلفة']) / df['التكلفة']) * 100

    # 2. حساب متوسط هامش ربح السوق العام للمنتجات المتوفرة
    avg_market_margin = df['هامش ربح السوق (%)'].mean()
    if pd.isna(avg_market_margin): avg_market_margin = 25.0 # قيمة افتراضية في حال عدم وجود بيانات نهائياً

    # 3. التنبؤ بسعر السوق للمنتجات التي لا توجد لها أسعار منافسين
    df['متوسط سعر المنافسين'] = df['متوسط السوق'].copy()
    mask_missing = df['متوسط السوق'].isna()
    # نستخدم التكلفة الأساسية للتنبؤ كنسبة مضافة عليها
    df.loc[mask_missing, 'متوسط سعر المنافسين'] = df.loc[mask_missing, 'التكلفة'] * (1 + avg_market_margin/100)
    df['حالة البيانات'] = df['متوسط السوق'].apply(lambda x: 'بيانات حقيقية' if pd.notna(x) else 'سعر متنبأ به')



    # منطق التسعير المقترح للانتشار (بناءً على السعر المرجعي سواء كان حقيقي أو متنبأ به)
    df['السعر المقترح'] = df['متوسط سعر المنافسين'] * (1 - target_discount/100)

    # التأكد من عدم تجاوز حد الربح الأدنى (نستخدم التكلفة الأساسية لكي يبقى السعر النهائي ثابتاً وتتأثر الأرباح بالمصاريف)
    df['سعر الحد الأدنى'] = df['التكلفة'] * (1 + min_profit_margin/100)
    df['السعر النهائي'] = df[['السعر المقترح', 'سعر الحد الأدنى']].max(axis=1)

    # حساب هامش الربح الفعلي بالسعر المقترح بعد أخذ التكلفة الشاملة في الاعتبار (نسبة مضافة على التكلفة)
    df['هامش الربح المتوقع (%)'] = ((df['السعر النهائي'] - df['التكلفة الشاملة']) / df['التكلفة الشاملة']) * 100

    # تصنيف وضع السعر
    def classify_price(row):
        if pd.isna(row['متوسط السوق']): return "تسعير بناءً على التنبؤ"
        if row['السعر النهائي'] < row['أقل سعر سوق']: return "الأرخص في السوق 🔥"
        if row['السعر النهائي'] < row['متوسط السوق']: return "سعر تنافسي"
        return "سعر متميز (Premium)"

    df['وضعية السعر'] = df.apply(classify_price, axis=1)

    # عرض مقاييس عامة ببطاقات أنيقة بعد اكتمال جميع الحسابات
    st.subheader("📊 تحليل بيانات السوق")
    num_predicted = mask_missing.sum()
    avg_expected_margin = df['هامش الربح المتوقع (%)'].mean()
    if pd.isna(avg_expected_margin): avg_expected_margin = 0.0

    cards_html = f"""
    <div style="display: flex; flex-wrap: wrap; gap: 15px; margin-bottom: 25px;">
        <div style="flex: 1 1 40%; min-width: 140px; background-color: #f8f9fa; padding: 10px 15px; border-radius: 10px; border-right: 5px solid #007bff; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
            <div style="color: #6c757d; font-size: 14px; font-weight: bold; margin-bottom: 5px;">
                📈 متوسط هامش السوق 
                <span title="يتم حسابه كنسبة مضافة على التكلفة (سعر المنافسين - التكلفة) / التكلفة.&#10;هذا المؤشر يعكس متوسط القوة التسعيرية للمنافسين." style="cursor:help; background:#007bff; color:white; border-radius:50%; padding:2px 7px; font-size:11px; margin-right:5px; display:inline-block; line-height:1;">!</span>
            </div>
            <h2 style="color: #007bff; margin: 0; font-size: 24px;">{avg_market_margin:.1f}%</h2>
        </div>
        <div style="flex: 1 1 40%; min-width: 140px; background-color: #f8f9fa; padding: 10px 15px; border-radius: 10px; border-right: 5px solid #17a2b8; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
            <div style="color: #6c757d; font-size: 14px; font-weight: bold; margin-bottom: 5px;">
                🎯 متوسط الربح المتوقع
            </div>
            <h2 style="color: #17a2b8; margin: 0; font-size: 24px;">{avg_expected_margin:.1f}%</h2>
        </div>
        <div style="flex: 1 1 40%; min-width: 140px; background-color: #f8f9fa; padding: 10px 15px; border-radius: 10px; border-right: 5px solid #28a745; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
            <div style="color: #6c757d; font-size: 14px; font-weight: bold; margin-bottom: 5px;">
                📦 عدد المنتجات
            </div>
            <h2 style="color: #28a745; margin: 0; font-size: 24px;">{len(df)}</h2>
        </div>
        <div style="flex: 1 1 40%; min-width: 140px; background-color: #f8f9fa; padding: 10px 15px; border-radius: 10px; border-right: 5px solid #ffc107; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
            <div style="color: #6c757d; font-size: 14px; font-weight: bold; margin-bottom: 5px;">
                🔮 المنتجات المتنبأ بها
            </div>
            <h2 style="color: #ffc107; margin: 0; font-size: 24px;">{num_predicted}</h2>
        </div>
    </div>
    """
    st.markdown(cards_html, unsafe_allow_html=True)

    # تحديد الأعمدة الرقمية لغرض التنسيق لاحقاً في العرض
    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns

    def generate_single_product_report(row, comp_data=None):
        base_cost = row['التكلفة']
    
        comp_count = len(comp_data) if comp_data else 0
    
        comp_html = ""
        if comp_count > 0:
            comp_df = pd.DataFrame(comp_data)
            comp_rows = "".join([f"<tr><td>{r['المنافس']}</td><td>{r['السعر']:.{decimals}f}</td><td dir='ltr'>{r['هامش الربح (%)']:.1f}%</td></tr>" for _, r in comp_df.iterrows()])
        
            warning_html = ""
            if comp_count == 1:
                warning_html = """
                <div style="background-color: #fff3cd; color: #856404; padding: 10px; border-radius: 5px; margin-bottom: 15px; border: 1px solid #ffeeba; font-size: 13px;">
                    ⚠️ <b>تنبيه:</b> يوجد سعر منافس وحيد فقط. يرجى التأكد من السعر المقترح حيث أن متوسط سعر المنافسين تم بناءً على بيانات محدودة.
                </div>
                """
            
            comp_html = f"""
            {warning_html}
            <h3 style="color: #495057; margin-top: 0;">🏢 أسعار وهوامش المنافسين</h3>
            <table dir="rtl" style="width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 14px; text-align: center;">
                <tr><th style="background-color: #f8f9fa; color: #333; border: 1px solid #ddd; padding: 10px;">المنافس</th><th style="background-color: #f8f9fa; color: #333; border: 1px solid #ddd; padding: 10px;">السعر</th><th style="background-color: #f8f9fa; color: #333; border: 1px solid #ddd; padding: 10px;">هامش الربح (%)</th></tr>
                {comp_rows}
            </table>
            <div style="display: flex; justify-content: space-around; background-color: #f8f9fa; padding: 15px; border-radius: 8px; margin-top: 15px; border: 1px solid #ddd;">
                <div style="text-align: center; font-size: 14px; font-weight: bold; color: #555;">أعلى سعر<br><span style="color:#dc3545">{comp_df['السعر'].max():.{decimals}f}</span></div>
                <div style="text-align: center; font-size: 14px; font-weight: bold; color: #555;">أدنى سعر<br><span style="color:#28a745">{comp_df['السعر'].min():.{decimals}f}</span></div>
                <div style="text-align: center; font-size: 14px; font-weight: bold; color: #555;">متوسط الهامش<br><span style="color:#007bff" dir="ltr">{comp_df['هامش الربح (%)'].mean():.1f}%</span></div>
            </div>
            """
        else:
            comp_html = """
            <h3 style="color: #495057; margin-top: 0;">🏢 أسعار وهوامش المنافسين</h3>
            <div style="background-color: #f8d7da; color: #721c24; padding: 15px; border-radius: 8px; border: 1px solid #f5c6cb; margin-bottom: 15px;">
                🚫 <b>لا توجد بيانات أسعار للمنافسين.</b> تم التنبؤ بالسعر المقترح لهذا الصنف بناءً على <b>متوسط هامش ربح السوق العام</b> مضافاً للتكلفة الأساسية.
            </div>
            """
        
        html = f"""
        <html dir="rtl" lang="ar">
        <head>
            <meta charset="utf-8">
            <title>تفاصيل المنتج {row['المنتج']}</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, sans-serif; padding: 20px; color: #333; }}
                h2 {{ color: #2c3e50; border-bottom: 2px solid #007bff; padding-bottom: 10px; }}
                td {{ border: 1px solid #ddd; padding: 10px; }}
                .container {{ display: flex; gap: 20px; margin-top: 20px; }}
                .col-right {{ flex: 1.2; }}
                .col-left {{ flex: 1; }}
                .analysis-box {{ background-color: #f8f9fa; padding: 15px; border-radius: 8px; border: 1px solid #ddd; line-height: 1.8; font-size: 14px; }}
                .analysis-row {{ display: flex; justify-content: space-between; border-bottom: 1px solid #e9ecef; padding-bottom: 8px; margin-bottom: 8px; }}
            </style>
        </head>
        <body>
            <h2>🏷️ تقرير منتج: {row['المنتج']}</h2>
            <div class="container">
                <div class="col-right">
                    {comp_html}
                </div>
                <div class="col-left">
                    <h3 style="color: #495057; margin-top: 0;">💡 تحليل التسعير الخاص بك</h3>
                    <div class="analysis-box">
                        <div class="analysis-row"><span>التكلفة الأساسية:</span> <strong>{base_cost:.{decimals}f}</strong></div>
                        <div class="analysis-row"><span>التكلفة الشاملة <span style="font-size:11px; color:#007bff;">(+{additional_expenses_pct}%)</span>:</span> <strong>{row['التكلفة الشاملة']:.{decimals}f}</strong></div>
                        <div class="analysis-row"><span>الحد الأدنى للبيع <span style="font-size:11px; color:#007bff;">(+{min_profit_margin}%)</span>:</span> <strong>{row['سعر الحد الأدنى']:.{decimals}f}</strong></div>
                        <div class="analysis-row"><span>متوسط سعر السوق:</span> <strong>{row['متوسط سعر المنافسين']:.{decimals}f}</strong></div>
                        <div class="analysis-row" style="background-color: #e2e3e5; padding: 5px; border-radius: 4px; margin-top: 5px;">
                            <span style="font-weight: bold;">السعر المقترح النهائي:</span> <strong style="color: #0056b3; font-size: 16px;">{row['السعر النهائي']:.{decimals}f}</strong>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-top: 8px;">
                            <span>الربح المتوقع:</span> <strong style="color: #28a745; font-size: 16px;" dir="ltr">{row['هامش الربح المتوقع (%)']:.1f}%</strong>
                        </div>
                        <div style="margin-top: 15px; text-align: center; padding-top: 10px; border-top: 1px dashed #ccc;">
                            📍 وضعية السعر: <b>{row['وضعية السعر']}</b>
                        </div>
                    </div>
                </div>
            </div>
            <p style="margin-top: 30px; text-align: center; color: #888; font-size: 12px;">تم إنشاء هذا التقرير بواسطة نظام التحليل والتسعير الذكي</p>
        </body>
        </html>
        """
        return html

    @st.dialog("🔍 تفاصيل وتحليل الصنف", width="large")
    def show_product_details_dialog(row):
        col_title, col_btn = st.columns([3, 1])
        col_title.markdown(f"**🏷️ المنتج:** `{row['المنتج']}`")
    
        base_cost = row['التكلفة']
        comp_data = []
        for comp in competitor_cols:
            comp_price = row.get(comp)
            if pd.notna(comp_price):
                margin = ((comp_price - base_cost) / base_cost) * 100
                comp_data.append({"المنافس": comp, "السعر": comp_price, "هامش الربح (%)": margin})
            
        # زر التنزيل
        dl_html = generate_single_product_report(row, comp_data)
        col_btn.download_button("📥 تنزيل تقرير المنتج", dl_html, file_name=f"product_{row['المنتج']}.html", mime="text/html", use_container_width=True)
    
        col1, col2 = st.columns([1.2, 1])
    
        comp_count = len(comp_data)
    
        with col1:
            st.markdown("**🏢 أسعار وهوامش المنافسين**")
        
            if comp_count > 0:
                if comp_count == 1:
                    st.warning("⚠️ **تنبيه:** يوجد سعر منافس وحيد فقط. يرجى التأكد من السعر المقترح حيث أن متوسط سعر المنافسين تم بناءً على بيانات محدودة.")
                
                comp_df = pd.DataFrame(comp_data)
                st.dataframe(comp_df.style.format({"السعر": f"{{:.{decimals}f}}", "هامش الربح (%)": "{:.1f}%"}), use_container_width=True, hide_index=True)
            
                metrics_html = f"""
                <div style="display: flex; gap: 10px; margin-top: 15px;">
                    <div style="flex: 1; background-color: #f8f9fa; padding: 10px; border-radius: 8px; border-right: 4px solid #dc3545; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                        <div style="color: #6c757d; font-size: 12px; font-weight: bold; margin-bottom: 5px;">أعلى سعر</div>
                        <h3 style="color: #dc3545; margin: 0; font-size: 18px;">{comp_df['السعر'].max():.{decimals}f}</h3>
                    </div>
                    <div style="flex: 1; background-color: #f8f9fa; padding: 10px; border-radius: 8px; border-right: 4px solid #28a745; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                        <div style="color: #6c757d; font-size: 12px; font-weight: bold; margin-bottom: 5px;">أدنى سعر</div>
                        <h3 style="color: #28a745; margin: 0; font-size: 18px;">{comp_df['السعر'].min():.{decimals}f}</h3>
                    </div>
                    <div style="flex: 1; background-color: #f8f9fa; padding: 10px; border-radius: 8px; border-right: 4px solid #007bff; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                        <div style="color: #6c757d; font-size: 12px; font-weight: bold; margin-bottom: 5px;">متوسط الهامش</div>
                        <h3 style="color: #007bff; margin: 0; font-size: 18px;" dir="ltr">{comp_df['هامش الربح (%)'].mean():.1f}%</h3>
                    </div>
                </div>
                """
                st.markdown(metrics_html, unsafe_allow_html=True)
            else:
                st.error("🚫 **لا توجد بيانات أسعار للمنافسين.** تم التنبؤ بالسعر المقترح لهذا الصنف بناءً على **متوسط هامش ربح السوق العام** مضافاً للتكلفة الأساسية.")
            
        with col2:
            st.markdown("**💡 تحليل التسعير الخاص بك**")
        
            analysis_html = f"""
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; border: 1px solid #e9ecef; font-size: 14px; margin-bottom: 15px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px; border-bottom: 1px solid #ddd; padding-bottom: 4px;">
                    <span style="color: #6c757d;">التكلفة الأساسية:</span> <strong>{base_cost:.{decimals}f}</strong>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px; border-bottom: 1px solid #ddd; padding-bottom: 4px;">
                    <span style="color: #6c757d;">التكلفة الشاملة <span style="font-size:11px; color:#007bff;">(+{additional_expenses_pct}%)</span>:</span> <strong>{row['التكلفة الشاملة']:.{decimals}f}</strong>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px; border-bottom: 1px solid #ddd; padding-bottom: 4px;">
                    <span style="color: #6c757d;">الحد الأدنى للبيع <span style="font-size:11px; color:#007bff;">(+{min_profit_margin}%)</span>:</span> <strong>{row['سعر الحد الأدنى']:.{decimals}f}</strong>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px; border-bottom: 1px solid #ddd; padding-bottom: 4px;">
                    <span style="color: #6c757d;">متوسط سعر السوق:</span> <strong>{row['متوسط سعر المنافسين']:.{decimals}f}</strong>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px; padding-bottom: 4px; background-color: #e2e3e5; padding: 5px; border-radius: 4px;">
                    <span style="color: #383d41; font-weight: bold;">السعر المقترح <span style="font-size:11px; color:#28a745;">(خصم {target_discount}%)</span>:</span> <strong style="color: #0056b3; font-size: 16px;">{row['السعر النهائي']:.{decimals}f}</strong>
                </div>
                <div style="display: flex; justify-content: space-between;">
                    <span style="color: #6c757d;">الربح المتوقع:</span> <strong style="color: #28a745; font-size: 16px;">{row['هامش الربح المتوقع (%)']:.1f}%</strong>
                </div>
            </div>
            """
            st.markdown(analysis_html, unsafe_allow_html=True)
            st.info(f"📍 وضعية السعر: **{row['وضعية السعر']}**")

    # --- ميزة فلترة الأعمدة وجدول النتائج ---
    st.info("💡 **إجراءات الجدول:** انقر على مربع الاختيار الصغير (Checkbox) بجوار اسم أي منتج في الجدول أدناه لفتح قائمة التفاصيل المنزلقة الخاصة به.")
    st.subheader("📋 نتائج التسعير النهائية")

    # وضع الفلاتر داخل قائمة منسدلة (Expander) لترتيب الواجهة
    with st.expander("⚙️ خيارات العرض والفلترة", expanded=False):
        f1, f2 = st.columns([1, 2])
        with f1:
            # فلتر وضعية السعر
            price_statuses = df['وضعية السعر'].unique()
            selected_statuses = st.multiselect("🔍 تصفية حسب وضعية السعر:", price_statuses, default=price_statuses)
        with f2:
            # فلتر إخفاء/إظهار الأعمدة
            all_display_cols = ['المنتج', 'التكلفة', 'التكلفة الشاملة', 'متوسط سعر المنافسين', 'السعر النهائي', 'هامش الربح المتوقع (%)', 'وضعية السعر', 'حالة البيانات']
            selected_cols = st.multiselect("👀 اختر الأعمدة التي تود عرضها في الجدول:", all_display_cols, default=all_display_cols)

    # تطبيق الفلتر على البيانات
    filtered_df = df[df['وضعية السعر'].isin(selected_statuses)] if selected_statuses else df

    if selected_cols:
        # إنشاء صف الإجماليات / المتوسطات
        summary_data = {'المنتج': '📊 المتوسط العام'}
        for col in all_display_cols:
            if col in numeric_cols and col in filtered_df.columns:
                summary_data[col] = filtered_df[col].mean()
            elif col != 'المنتج':
                summary_data[col] = ''
    
        summary_df = pd.DataFrame([summary_data])
        display_df = pd.concat([filtered_df, summary_df], ignore_index=True)
    
        # ضبط الفهرس ليظهر بشكل جميل مع صف المتوسط
        display_index = list(range(1, len(filtered_df) + 1)) + ['-']
        # دمج عمود الفهرس (م) كأول عمود ليتم عكسه إلى اليمين
        display_df.insert(0, 'م', display_index)

        # تهيئة تنسيق الأرقام لعرض الخانات العشرية المطلوبة فقط
        numeric_display_cols = [c for c in selected_cols if c in numeric_cols]
        format_dict = {c: f"{{:.{decimals}f}}" for c in numeric_display_cols}
    
        # إعداد ترتيب الأعمدة ليكون متوافقاً مع شاشات الجوال 
        # (يظهر رقم التسلسل واسم المنتج في البداية من اليسار لكي لا يضطر المستخدم للتمرير)
        display_cols_rtl = ['م'] + selected_cols
        reversed_cols = display_cols_rtl
    
        # إعداد خصائص الأعمدة لتوسعة عمود المنتج بشكل معقول لتفادي التمرير الأفقي
        col_config = {
            "المنتج": st.column_config.TextColumn("المنتج", width="medium")
        }

        # حفظ التحديد الأخير لتجنب فتح النافذة عند الضغط على أزرار التصدير
        if 'last_selection' not in st.session_state:
            st.session_state.last_selection = []
            
        event = st.dataframe(
            display_df[reversed_cols].style.format(format_dict).highlight_max(subset=numeric_display_cols, axis=0), 
            use_container_width=True,
            hide_index=True,
            column_config=col_config,
            on_select="rerun",
            selection_mode="single-row"
        )
    
        # عند اختيار صف (منتج) من الجدول
        current_selection = event.selection.rows if hasattr(event, 'selection') else []
        if current_selection and current_selection != st.session_state.last_selection:
            st.session_state.last_selection = current_selection
            selected_idx = current_selection[0]
            # نتأكد أنه لم يتم اختيار صف "المتوسط العام" الأخير
            if selected_idx < len(filtered_df):
                selected_row = filtered_df.iloc[selected_idx]
                show_product_details_dialog(selected_row)
        else:
            # تحديث حالة التحديد حتى لو تم إلغاء التحديد
            st.session_state.last_selection = current_selection
    
        # إظهار مؤشر نسبة المصاريف الإضافية أسفل الجدول
        if additional_expenses_pct > 0:
            st.info(f"💡 **ملاحظة:** تم تضمين نسبة مصاريف إضافية قدرها **{additional_expenses_pct}%** في حساب 'التكلفة الشاملة'، وجميع هوامش الربح المتوقعة أعلاه محسوبة بعد خصم هذه المصاريف.")
        else:
            st.info("💡 **ملاحظة:** لا توجد مصاريف إضافية مسجلة. (التكلفة = التكلفة الشاملة).")

        # أزرار التصدير
        col_export1, col_export2 = st.columns(2)
    
        # --- تصدير إلى Excel بتنسيق جدول ---
        def convert_df_to_excel(df_to_export):
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df_to_export.to_excel(writer, index=False, sheet_name='النتائج')
                workbook = writer.book
                worksheet = writer.sheets['النتائج']
                worksheet.right_to_left() # من اليمين لليسار
                # تحويل البيانات إلى جدول Excel
                max_row, max_col = df_to_export.shape
                column_settings = [{'header': column} for column in df_to_export.columns]
                worksheet.add_table(0, 0, max_row, max_col - 1, {'columns': column_settings, 'style': 'Table Style Medium 2'})
                worksheet.set_column(0, max_col - 1, 15) # توسيع الأعمدة
            return output.getvalue()
    
        with col_export1:
            excel_data = convert_df_to_excel(display_df[selected_cols])
            st.download_button(
                label="📥 تصدير الجدول إلى Excel",
                data=excel_data,
                file_name='نتائج_التسعير.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                use_container_width=True
            )
        
        with col_export2:
            # --- تصدير إلى HTML لغرض الطباعة كـ PDF ---
            # تقرير الـ HTML يوفر دعماً ممتازاً للغة العربية مقارنة بمكتبات الـ PDF المباشرة
            def generate_html_report(df_to_export):
                # تنسيق الأرقام في التقرير
                formatted_df = df_to_export.copy()
                for c in numeric_display_cols:
                    formatted_df[c] = formatted_df[c].apply(lambda x: f"{x:.{decimals}f}" if pd.notna(x) and type(x) != str else x)
            
                html = f"""
                <html dir="rtl" lang="ar">
                <head>
                    <meta charset="utf-8">
                    <title>تقرير التسعير</title>
                    <style>
                        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding: 20px; }}
                        h2 {{ text-align: center; color: #2c3e50; }}
                        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 14px; }}
                        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: center; }}
                        th {{ background-color: #007bff; color: white; }}
                        tr:last-child {{ font-weight: bold; background-color: #e9ecef; }}
                        .summary {{ display: flex; justify-content: space-around; background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px; border: 1px solid #ddd; }}
                        .summary-item {{ text-align: center; font-size: 16px; font-weight: bold; color: #333; }}
                        .footer {{ margin-top: 30px; font-size: 12px; color: #777; text-align: center; }}
                    </style>
                </head>
                <body>
                    <h2>💡 تقرير تحليل وتسعير المنتجات</h2>
                    <div class="summary">
                        <div class="summary-item">متوسط هامش السوق<br><span style="color:#007bff">{avg_market_margin:.1f}%</span></div>
                        <div class="summary-item">متوسط الربح المتوقع<br><span style="color:#17a2b8">{avg_expected_margin:.1f}%</span></div>
                        <div class="summary-item">المصاريف الإضافية<br><span style="color:#007bff">{additional_expenses_pct}%</span></div>
                        <div class="summary-item">الحد الأدنى للربح<br><span style="color:#007bff">{min_profit_margin}%</span></div>
                    </div>
                    <table>
                        <thead>
                            <tr>{"".join(f"<th>{col}</th>" for col in formatted_df.columns)}</tr>
                        </thead>
                        <tbody>
                            {"".join("<tr>" + "".join(f"<td>{val if pd.notna(val) else ''}</td>" for val in row) + "</tr>" for row in formatted_df.values)}
                        </tbody>
                    </table>
                    <div class="footer">
                        تم إنشاء هذا التقرير آلياً بواسطة منصة تسعير المنتجات الذكية.<br>
                        (يمكنك طباعة هذه الصفحة مباشرة أو حفظها كملف PDF بالضغط على Ctrl+P واختيار حفظ كـ PDF)<br><br>
                        جميع الحقوق محفوظة لـ <b>AMR AL-MATARI</b> | 📧 E-MAIL: amralmatari@gmail.com
                    </div>
                </body>
                </html>
                """
                return html.encode('utf-8')
            
            html_report_data = generate_html_report(display_df[selected_cols])
            st.download_button(
                label="🖨️ تصدير التقرير للطباعة (PDF / HTML)",
                data=html_report_data,
                file_name='تقرير_التسعير.html',
                mime='text/html',
                use_container_width=True
            )
    else:
        st.warning("يرجى اختيار عمود واحد على الأقل للعرض.")

    # الرسوم البيانية
    st.markdown("<h3 style='margin-top: 30px; border-bottom: 2px solid #eee; padding-bottom: 10px;'>📈 التحليل البصري</h3>", unsafe_allow_html=True)
    
    chart_tab1, chart_tab2, chart_tab3 = st.tabs(["📊 مقارنة الأسعار", "🍩 وضعية المنتجات", "📉 هوامش الربح"])
    
    # إبقاء أيقونة التنزيل مع إخفاء شعار Plotly، وتعطيل التقريب باللمس/الماوس الافتراضي
    chart_config = {'displaylogo': False, 'scrollZoom': False}
    
    with chart_tab1:
        fig1 = px.bar(df, x='المنتج', y=['متوسط سعر المنافسين', 'السعر النهائي', 'التكلفة الشاملة'], 
                     barmode='group', height=400, color_discrete_sequence=['#ff9f43', '#00d2d3', '#54a0ff'])
        fig1.update_layout(title="مقارنة منتجاتنا مقابل السوق والتكلفة", font=dict(family="Tahoma"),
                           xaxis_title="", yaxis_title="السعر", legend_title="", margin=dict(t=50, l=10, r=10, b=80),
                           legend=dict(orientation="h", yanchor="top", y=-0.3, xanchor="center", x=0.5),
                           dragmode=False)
        st.plotly_chart(fig1, use_container_width=True, config=chart_config)

    with chart_tab2:
        fig2 = px.pie(df, names='وضعية السعر', hole=0.4, height=400, 
                      color_discrete_sequence=px.colors.qualitative.Pastel)
        fig2.update_layout(title="توزيع وضعية منتجاتنا في السوق", font=dict(family="Tahoma"), margin=dict(t=50, l=10, r=10, b=50),
                           legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="center", x=0.5),
                           dragmode=False)
        st.plotly_chart(fig2, use_container_width=True, config=chart_config)

    with chart_tab3:
        fig3 = px.line(df, x='المنتج', y=['هامش الربح المتوقع (%)', 'هامش ربح السوق (%)'], markers=True, height=400,
                       color_discrete_sequence=['#10ac84', '#ee5253'])
        fig3.update_layout(title="مقارنة هامش ربحنا المتوقع مقابل هامش ربح السوق", font=dict(family="Tahoma"),
                           xaxis_title="", yaxis_title="هامش الربح (%)", legend_title="", margin=dict(t=50, l=10, r=10, b=80),
                           legend=dict(orientation="h", yanchor="top", y=-0.3, xanchor="center", x=0.5),
                           dragmode=False)
        st.plotly_chart(fig3, use_container_width=True, config=chart_config)

else:
    # دليل الاستخدام عند عدم وجود ملف
    st.markdown("""
        <div style="background-color: #f8f9fa; padding: 30px; border-radius: 10px; margin-top: 20px; text-align: right; border-right: 5px solid #007bff;">
            <h2 style="color: #2c3e50; margin-bottom: 20px;">👋 مرحباً بك في منصة تسعير المنتجات الذكية!</h2>
            <p style="font-size: 18px; color: #555;">هذه المنصة صممت خصيصاً لمساعدتك في تحليل أسعار المنافسين وبناء استراتيجية تسعير ذكية ومربحة لمنتجاتك. للبدء، يرجى اتباع الخطوات البسيطة التالية:</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.write("") # spacer
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
            <div style="text-align: center; padding: 15px; background: white; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); height: 100%;">
                <h1 style="font-size: 35px; margin: 0;">📥</h1>
                <h3 style="color: #007bff; font-size: 18px;">1. تنزيل القالب</h3>
                <p style="color: #666; font-size: 13px;">قم بتنزيل قالب الإكسل من تبويب البيانات.</p>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
            <div style="text-align: center; padding: 15px; background: white; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); height: 100%;">
                <h1 style="font-size: 35px; margin: 0;">📤</h1>
                <h3 style="color: #007bff; font-size: 18px;">2. رفع البيانات</h3>
                <p style="color: #666; font-size: 13px;">قم بملء القالب وارفع الملف للتطبيق.</p>
            </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
            <div style="text-align: center; padding: 15px; background: white; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); height: 100%;">
                <h1 style="font-size: 35px; margin: 0;">⚙️</h1>
                <h3 style="color: #007bff; font-size: 18px;">3. ضبط التسعير</h3>
                <p style="color: #666; font-size: 13px;">انتقل لتبويب التسعير لضبط هوامش الربح.</p>
            </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
            <div style="text-align: center; padding: 15px; background: white; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); height: 100%;">
                <h1 style="font-size: 35px; margin: 0;">📊</h1>
                <h3 style="color: #007bff; font-size: 18px;">4. استعراض التحليل</h3>
                <p style="color: #666; font-size: 13px;">استعرض مؤشرات الأداء، تفاصيل المنتجات والرسوم.</p>
            </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br><hr>", unsafe_allow_html=True)
    st.info("💡 **تلميح:** يمكنك دائماً تصدير النتائج النهائية والتقارير إلى ملفات PDF أو Excel بعد إتمام التحليل لمشاركتها مع فريقك.")

# تذييل حقوق النشر (يظهر في جميع الحالات)
st.markdown("""
<div style="text-align: center; margin-top: 30px; margin-bottom: 20px; padding-top: 15px; border-top: 1px solid #eaeaea; color: #6c757d; font-size: 13px; direction: rtl;">
    جميع الحقوق محفوظة لـ <b>AMR AL-MATARI</b> &nbsp;|&nbsp; 📧 E-MAIL: <a href="mailto:amralmatari@gmail.com" style="color: #007bff; text-decoration: none; font-family: Tahoma, sans-serif;">amralmatari@gmail.com</a>
</div>
""", unsafe_allow_html=True)