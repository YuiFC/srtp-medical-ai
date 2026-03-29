import{L as e,Ut as t,_ as n,ct as r,d as i,et as a,m as o,ot as s,p as c,t as l}from"./_plugin-vue_export-helper-DPFtWm_A.js";import{n as u,t as d}from"./index-BjoTqRaS.js";var f={class:`page-container`},p={class:`content-card`},m={class:`form-section`},h={class:`form-group`},g={class:`form-group`},_={class:`form-actions`},v=[`disabled`],y={key:0,class:`result-section`},b=[`innerHTML`],x=l({__name:`TextReportView`,setup(l){let x=r(!1),S=r(``),C=s({reportText:``,examType:``}),w=async()=>{if(!C.reportText){alert(`请输入报告文本`);return}x.value=!0,setTimeout(()=>{S.value=`
      <div class="result-item">
        <h4>🔍 报告分析</h4>
        <p><strong>检查类型：</strong>${{chest_xray:`胸部X光`,chest_ct:`胸部CT`,abdomen_ct:`腹部CT`,head_ct:`头颅CT`,other:`其他`}[C.examType]||`未指定`}</p>
      </div>
      <div class="result-item">
        <h4>📋 主要发现</h4>
        <p>${C.reportText.substring(0,300)}${C.reportText.length>300?`...`:``}</p>
      </div>
      <div class="result-item">
        <h4>💡 健康建议</h4>
        <ul>
          <li>建议定期复查，监测病情变化</li>
          <li>如有不适，请及时就医</li>
          <li>保持健康生活方式</li>
        </ul>
      </div>
      <div class="result-note">
        <h4>🧠 解读说明</h4>
        <p>本分析基于纯文本LLM，仅供参考，不作为医疗诊断依据。</p>
      </div>
    `,x.value=!1,alert(`分析完成`)},1500)},T=()=>{C.reportText=``,C.examType=``,S.value=``},E=()=>{let e=new Blob([S.value.replace(/<[^>]*>/g,``)],{type:`text/plain`}),t=URL.createObjectURL(e),n=document.createElement(`a`);n.href=t,n.download=`medical-report-analysis-${Date.now()}.txt`,n.click(),URL.revokeObjectURL(t)},D=()=>{let e=S.value.replace(/<[^>]*>/g,``).replace(/\s+/g,` `).trim();navigator.clipboard.writeText(e).then(()=>{alert(`已复制到剪贴板`)}).catch(()=>{alert(`复制失败，请手动复制`)})};return(r,s)=>(e(),o(`div`,f,[s[6]||=i(`div`,{class:`page-header`},[i(`h1`,null,`📄 放射学报告文本解读`),i(`p`,null,`输入放射学报告，使用LLM进行智能解读分析`)],-1),i(`div`,p,[i(`div`,m,[i(`div`,h,[s[2]||=i(`label`,{class:`form-label`},`放射学报告文本`,-1),a(i(`textarea`,{"onUpdate:modelValue":s[0]||=e=>C.reportText=e,class:`form-textarea`,placeholder:`请输入放射学报告内容...

例如：胸部CT检查：双肺可见多个大小不等结节，最大者位于右肺上叶，直径约1.2cm，边界清晰...`},null,512),[[u,C.reportText]])]),i(`div`,g,[s[4]||=i(`label`,{class:`form-label`},`检查类型`,-1),a(i(`select`,{"onUpdate:modelValue":s[1]||=e=>C.examType=e,class:`form-select`},[...s[3]||=[n(`<option value="" data-v-774252e3>请选择检查类型</option><option value="chest_xray" data-v-774252e3>胸部X光</option><option value="chest_ct" data-v-774252e3>胸部CT</option><option value="abdomen_ct" data-v-774252e3>腹部CT</option><option value="head_ct" data-v-774252e3>头颅CT</option><option value="other" data-v-774252e3>其他</option>`,6)]],512),[[d,C.examType]])]),i(`div`,_,[i(`button`,{class:`btn-primary`,onClick:w,disabled:x.value},t(x.value?`分析中...`:`AI解读分析`),9,v),i(`button`,{class:`btn-secondary`,onClick:T},`重置`)])]),S.value?(e(),o(`div`,y,[s[5]||=i(`h3`,null,`📊 AI解读结果`,-1),i(`div`,{class:`result-content`,innerHTML:S.value},null,8,b),i(`div`,{class:`result-actions`},[i(`button`,{class:`btn-outline`,onClick:E},`保存结果`),i(`button`,{class:`btn-outline`,onClick:D},`复制`)])])):c(``,!0)])]))}},[[`__scopeId`,`data-v-774252e3`]]);export{x as default};