import{Bt as e,L as t,Ut as n,_ as r,a as i,ct as a,d as o,et as s,m as c,ot as l,p as u,t as d,z as f}from"./_plugin-vue_export-helper-DPFtWm_A.js";import{i as p,n as m,r as h,t as g}from"./index-BjoTqRaS.js";var _={class:`page-container`},v={class:`content-card`},y={class:`form-section`},b={class:`form-row`},x={class:`form-col`},S={class:`form-group`},C={key:0,class:`upload-placeholder`},w={key:1,class:`upload-preview`},T={class:`preview-name`},E=[`onClick`],D={class:`form-col`},O={class:`form-group`},k={class:`form-group`},A={class:`form-actions`},j=[`disabled`],M={key:0,class:`result-section`},N={class:`result-tabs`},P={class:`tab-content`},F=[`innerHTML`],I=[`innerHTML`],L=[`innerHTML`],R=d({__name:`MultimodalView`,setup(d){let R=a(!1),z=a(`image`),B=a(null),V=a(null),H=l({imageList:[],reportText:``,examType:``}),U=()=>{B.value.click()},W=e=>{let t=Array.from(e.target.files);H.imageList=[...H.imageList,...t]},G=e=>{H.imageList.splice(e,1)},K=async()=>{if(!H.reportText&&H.imageList.length===0){alert(`请上传影像或输入报告文本`);return}R.value=!0,setTimeout(()=>{V.value={imageAnalysis:`
        <div class="result-item">
          <h4>📷 影像特征分析</h4>
          <ul>
            <li>检测到多处异常信号影</li>
            <li>最大病灶约1.2cm，位于右肺上叶</li>
            <li>边界清晰，密度均匀</li>
            <li>未见明显胸腔积液</li>
          </ul>
        </div>
      `,textAnalysis:`
        <div class="result-item">
          <h4>📄 报告文本解读</h4>
          <ul>
            <li>双肺多发结节</li>
            <li>最大结节位于右肺上叶</li>
            <li>建议定期复查</li>
          </ul>
        </div>
      `,combined:`
        <div class="result-item">
          <h4>🔗 联合分析结论</h4>
          <p>基于影像和文本的联合分析，建议：</p>
          <ul>
            <li><strong>综合评估：</strong>影像表现与报告描述一致</li>
            <li><strong>复查建议：</strong>3个月后复查CT对比</li>
            <li><strong>注意事项：</strong>如有咳嗽、胸痛等症状请及时就医</li>
          </ul>
        </div>
        <div class="result-note">
          ⚠️ 本分析仅供参考，不作为医疗诊断依据
        </div>
      `},R.value=!1,alert(`多模态分析完成`)},2e3)},q=()=>{H.imageList=[],H.reportText=``,H.examType=``,V.value=null};return(a,l)=>(t(),c(`div`,_,[l[11]||=o(`div`,{class:`page-header`},[o(`h1`,null,`🖼️ 多模态AI解读`),o(`p`,null,`上传医学影像 + 报告文本，多模态AI联合分析`)],-1),o(`div`,v,[o(`div`,y,[o(`div`,b,[o(`div`,x,[o(`div`,S,[l[6]||=o(`label`,{class:`form-label`},`上传医学影像`,-1),o(`div`,{class:`upload-area`,onClick:U},[o(`input`,{type:`file`,ref_key:`fileInput`,ref:B,onChange:W,accept:`image/*`,multiple:``,style:{display:`none`}},null,544),H.imageList.length===0?(t(),c(`div`,C,[...l[5]||=[o(`span`,{class:`upload-icon`},`📁`,-1),o(`p`,null,`点击上传或拖拽文件`,-1),o(`p`,{class:`upload-hint`},`支持 X光、CT 等医学影像`,-1)]])):(t(),c(`div`,w,[(t(!0),c(i,null,f(H.imageList,(e,r)=>(t(),c(`div`,{key:r,class:`preview-item`},[o(`span`,T,n(e.name),1),o(`span`,{class:`preview-remove`,onClick:p(e=>G(r),[`stop`])},`×`,8,E)]))),128))]))])])]),o(`div`,D,[o(`div`,O,[l[7]||=o(`label`,{class:`form-label`},`放射学报告文本`,-1),s(o(`textarea`,{"onUpdate:modelValue":l[0]||=e=>H.reportText=e,class:`form-textarea`,placeholder:`请输入报告文本...`},null,512),[[m,H.reportText]])])])]),o(`div`,k,[l[9]||=o(`label`,{class:`form-label`},`检查类型`,-1),s(o(`select`,{"onUpdate:modelValue":l[1]||=e=>H.examType=e,class:`form-select`},[...l[8]||=[r(`<option value="" data-v-1bba9f69>请选择检查类型</option><option value="chest_xray" data-v-1bba9f69>胸部X光</option><option value="chest_ct" data-v-1bba9f69>胸部CT</option><option value="abdomen_ct" data-v-1bba9f69>腹部CT</option><option value="head_ct" data-v-1bba9f69>头颅CT</option>`,5)]],512),[[g,H.examType]])]),o(`div`,A,[o(`button`,{class:`btn-primary`,onClick:K,disabled:R.value},n(R.value?`分析中...`:`多模态AI联合分析`),9,j),o(`button`,{class:`btn-secondary`,onClick:q},`重置`)])]),V.value?(t(),c(`div`,M,[l[10]||=o(`h3`,null,`🧠 多模态AI分析结果`,-1),o(`div`,N,[o(`button`,{class:e([`tab-btn`,{active:z.value===`image`}]),onClick:l[2]||=e=>z.value=`image`},` 📷 影像分析 `,2),o(`button`,{class:e([`tab-btn`,{active:z.value===`text`}]),onClick:l[3]||=e=>z.value=`text`},` 📄 文本分析 `,2),o(`button`,{class:e([`tab-btn`,{active:z.value===`combined`}]),onClick:l[4]||=e=>z.value=`combined`},` 🔗 联合结论 `,2)]),o(`div`,P,[s(o(`div`,{innerHTML:V.value.imageAnalysis},null,8,F),[[h,z.value===`image`]]),s(o(`div`,{innerHTML:V.value.textAnalysis},null,8,I),[[h,z.value===`text`]]),s(o(`div`,{innerHTML:V.value.combined},null,8,L),[[h,z.value===`combined`]])])])):u(``,!0)])]))}},[[`__scopeId`,`data-v-1bba9f69`]]);export{R as default};