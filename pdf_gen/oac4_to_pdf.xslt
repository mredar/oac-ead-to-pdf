<xsl:stylesheet 
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
  xmlns:saxon="http://icl.com/saxon" 
  xmlns:editURL="http://cdlib.org/xtf/editURL"
  xmlns:xtf="http://cdlib.org/xtf"
  xmlns:pdf="http://www.adobe.com/pdf/"
  extension-element-prefixes="saxon" 
  xmlns:tmpl="xslt://template"
  exclude-result-prefixes="#all"
  version="2.0">
  
<!-- BSD license copyright 2009 -->
  <xsl:strip-space elements="*"/>
  
<!-- DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd" -->

  <xsl:output method="xhtml"
    indent="yes"
    encoding="utf-8"
    media-type="text/html; charset=UTF-8" 
	omit-xml-declaration="yes"
    />
<!--
              doctype-public="-//W3C//DTD XHTML 1.0 Transitional//EN"
              doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"/>
          -->
  
    <xsl:include
        href="./xsl/docFormatterCommon.xsl"/>
    <xsl:include
        href="./xsl/parameter.xsl"/>
    <xsl:include
        href="./xsl/editURL.xsl"/>
    <xsl:include href="./xsl/SSI.xsl"/>
    <xsl:include href="./xsl/table.html.xsl"/>
    <xsl:include href="./xsl/ead.html.xsl"/>
    <xsl:include href="./xsl/online-items-graphic-element.xsl"/>
  
  <xsl:key name="hit-num-dynamic" match="xtf:hit" use="@hitNum"/>
  <xsl:key name="hit-rank-dynamic" match="xtf:hit" use="@rank"/>
  <xsl:key name="hasContent" match="*[@id][.//dao|.//daogrp]" use="@id"/>

  <xsl:key name="not.archdesc" match="*[@id][not(ancestor-or-self::archdesc)]" use="@id"/>
  <xsl:key name="archdesc" match="archdesc[@id]|archdesc/*[@id][not(ancestor-or-self::dsc)]" use="@id"/>
  <xsl:key name="dsc" match="dsc[@id]|dsc/*[@id]" use="@id"/>

<xsl:key name="daos" match="*[did/daogrp] | *[did/dao]" >
        <xsl:value-of select="@ORDER"/>
</xsl:key>

 <xsl:param name="http.URL"/> 

<xsl:param name="view"/>
<xsl:param name="style"/>
<xsl:param name="pdfgen" select="'1'"/>

<!--         .label { font-weight:bold; width: 10% !important; }     
        .item { padding: .5em; } -->




<xsl:variable name="page" select="/"/>

<xsl:template match="/">
<html>
<head>
    <!-- Pisa PDF generator doesn't seem to use this.
    no difference in PDF when below commented out. It looks as though
    you have to pass the pisaDocument function a default_css as a string-->
    <!--
    <link rel="stylesheet" href="./includes/css/oac.css"></link>
    -->
<style>
    <xsl:choose>
        <xsl:when test="$pdfgen!=''">
    <xsl:apply-templates select="$page" mode="pdf-head"/>
    <xsl:apply-templates select="$page/ead/archdesc/dsc" mode="pdf-head"/>
</xsl:when>
</xsl:choose>
</style>
</head>
<body>


            <xsl:call-template name='pdfbodyhead' />


        <div class="collection-admin-view">
            <xsl:apply-templates select="$page/ead/frontmatter" mode="ead"/>
            <xsl:if test="$page/ead/frontmatter">
                <hr/>
            </xsl:if>

            <xsl:apply-templates select="$page/ead/archdesc/*[not(self::dsc)]" mode="ead"/>
	</div>
	<div class="collection-contents">
                       <xsl:apply-templates select="$page/ead/archdesc/dsc" mode="pdfStart"/>
	</div>
</body>
</html>


</xsl:template>


<xsl:template match="dsc" mode="pdfStart">
    <xsl:if test="$pdfgen!=''">
    <xsl:variable name="dscID" ><xsl:value-of select="translate(@id, '.', '_')"/></xsl:variable>
    <pdf:nexttemplate name="sec_{$dscID}" />
    <div class="pdf-header" id="header_{$dscID}" >
        <xsl:apply-templates select="head" />
    </div>
    <div class="pdf-header" id="subheader_{$dscID}" ></div>
    </xsl:if>
    <xsl:variable 
    	name="NoSeries"
        select = "not(boolean(
                         /ead/archdesc/dsc/c01[@level='subseries'] or
                         /ead/archdesc/dsc/c01[@level='recordgrp'] or
                         /ead/archdesc/dsc/c01[@level='collection'] or
                         /ead/archdesc/dsc/c01/c02[@level='subseries'] or
                         /ead/archdesc/dsc/c01/c02[@level='recordgrp'] or
                         /ead/archdesc/dsc/c01/c02[@level='collection']
        ))"
                         />
    <!--
    <xsl:message>
        NoSeries = <xsl:copy-of select='$NoSeries'/>
    </xsl:message>
    -->
    <xsl:apply-templates mode="pdf"
        select="c01|c02|c03|c04|c05|c06|c07|c08|c09|c10|c11|c12">
        <xsl:with-param name="tableStart" select="$NoSeries"/>
    </xsl:apply-templates>

</xsl:template>




  <!-- default match identity transform -->

  <xsl:template match="*">
	        <xsl:element name="{name(.)}">
              <xsl:for-each select="@*">
                  <xsl:attribute name="{name(.)}">
                      <xsl:value-of select="."/>
                  </xsl:attribute>
              </xsl:for-each>
              <xsl:apply-templates/>
          </xsl:element>
  </xsl:template>

<xsl:template name='pdfbodyhead'>
    <xsl:variable name="pdf-header-background-0" select="if ($pdfgen='debug')
        then 'background-color: orange;' else ''">
    </xsl:variable>
    <xsl:variable name="pdf-footer-background-left" select="if ($pdfgen='debug')
        then 'background-color: orange;' else ''">
    </xsl:variable>
    <xsl:variable name="pdf-footer-background-mid" select="if ($pdfgen='debug')
        then 'background-color: red;' else ''">
    </xsl:variable>
    <xsl:variable name="pdf-footer-background-right" select="if ($pdfgen='debug')
        then 'background-color: yellow;' else ''">
    </xsl:variable>
    <pdf:nexttemplate name='front_matter' />
    <div id="front_matter_header"></div>
    <div id="header_hr"><hr/></div>
    <div id="footer_hr"><hr/></div>
    <div id="footer_left" style="text-align: left;{$pdf-footer-background-left}">
            <xsl:value-of select="$page/ead/archdesc/did/unittitle"/>
    </div>
    <div id="footer_mid" style="text-align:center;{$pdf-footer-background-mid}">
            <xsl:apply-templates select="$page/ead/archdesc/did/unitid" mode="collectionId"/>
    </div>
    <div id="footer_right" style
        ="text-align:right;{$pdf-footer-background-right}">
        <pdf:pagenumber />
    </div>

    <div id="header_img">
        <img class="icon" alt="[Online Archive of California]" border="0"
            src="some_logo_file.png" />
    </div>
    <!--
    <div id="header_main" style="text-align: left; {$pdf-header-background-0};">
        -->
    <xsl:variable 
    	name="NoSeries"
        select = "not(boolean(
                         /ead/archdesc/dsc/c01[@level='subseries'] or
                         /ead/archdesc/dsc/c01[@level='recordgrp'] or
                         /ead/archdesc/dsc/c01[@level='collection'] or
                         /ead/archdesc/dsc/c01/c02[@level='subseries'] or
                         /ead/archdesc/dsc/c01/c02[@level='recordgrp'] or
                         /ead/archdesc/dsc/c01/c02[@level='collection']
        ))"
    />
    <div id="header_main">
        <xsl:choose>
            <xsl:when test="not($NoSeries)">
                <xsl:variable 
                	name="pdfOutlineStyle" 
                    select="concat('-pdf-outline: true;', ' ',
                        '-pdf-outline-open: true;', ' ',
                        '-pdf-outline-level: 0',
                        '; '
                   )"
                 />
                <xsl:attribute name='style' select="concat('text-align: left; ',
                    $pdfOutlineStyle,
                    $pdf-header-background-0, ';'
                    )"/>
            </xsl:when>
            <xsl:otherwise>
                <xsl:attribute name='style' select="concat('text-align: left; ',
                    $pdf-header-background-0, ';'
                    )"/>
            </xsl:otherwise>
        </xsl:choose>
        
	    <xsl:apply-templates select="$page/ead/eadheader/filedesc/titlestmt/titleproper[1]" mode="ead"/>
        <br/>
	    <xsl:variable name="ark" select="($page)/ead/eadheader/eadid/@identifier"/>
        <a
            href="http://oac.cdlib.org/findaid/{$ark}">http://oac.cdlib.org/findaid/<xsl:value-of select="$ark"/></a>
    </div>
</xsl:template>

<xsl:template match="/" mode="pdf-head">
    <xsl:variable name="pdf-frame-border" select="if ($pdfgen='debug') then '-pdf-frame-border: 1;' else ''">
    </xsl:variable>

    @page {
	size: letter;	
	margin-top: 2.5cm;
	margin-left: 3cm;
	margin-right: 2cm;
	margin-bottom: 3cm;
    <xsl:value-of select="$pdf-frame-border"/>

    @frame header_img {
        -pdf-frame-content: header_img;
        top: .5cm;
        left: 2cm;
        right: 16cm;
        height: 1.25cm;
        <xsl:value-of select="$pdf-frame-border"/>
    }

    @frame header_main {
        -pdf-frame-content: header_main;
        top: .5cm;
        left: 6cm;
        right: 2cm;
        height: 1.25cm;
        <xsl:value-of select="$pdf-frame-border"/>
    }

    @frame header_hr {
    -pdf-frame-content: header_hr;
		top: 2.25cm;
		left: 2cm;
		right: 2cm;
		height: .25cm;		
        <xsl:value-of select="$pdf-frame-border"/>
	}
        
    @frame footer_left {
        -pdf-frame-content: footer_left;
        bottom: 1cm;
		left: 2cm;
		right: 14cm;
        height: 1.5cm;
        <xsl:value-of select="$pdf-frame-border"/>
    }
    @frame footer_mid {
        -pdf-frame-content: footer_mid;
        bottom: 1cm;
		left: 8cm;
		right: 5cm;
        height: 1.5cm;
        <xsl:value-of select="$pdf-frame-border"/>
    }
    @frame footer_right {
        -pdf-frame-content: footer_right;
        bottom: 1cm;
		left: 17cm;
		right: 2cm;
        height: 1.5cm;
        <xsl:value-of select="$pdf-frame-border"/>
    }
	
    @frame footer_hr {
        -pdf-frame-content: footer_hr;
        bottom: 2.7cm;
		left: 2cm;
		right: 2cm;
        height: 0.25cm;
        <xsl:value-of select="$pdf-frame-border"/>
    }
}

@page front_matter {
	size: letter;	
	margin-top: 2.5cm;
	margin-left: 3cm;
	margin-right: 2cm;
	margin-bottom: 3cm;
    <xsl:value-of select="$pdf-frame-border"/>

	@frame header {
        -pdf-frame-content: front_matter_header;
		top: .5cm;
		left: 2cm;
		right: 2cm;
		height: 1.25cm;		
        <xsl:value-of select="$pdf-frame-border"/>
	}

    @frame header_hr {
    -pdf-frame-content: header_hr;
		top: 2.25cm;
		left: 2cm;
		right: 2cm;
		height: .25cm;		
        <xsl:value-of select="$pdf-frame-border"/>
	}
        

    @frame footer_left {
        -pdf-frame-content: footer_left;
        bottom: 1cm;
		left: 2cm;
		right: 14cm;
        height: 1.5cm;
        <xsl:value-of select="$pdf-frame-border"/>
    }
    @frame footer_mid {
        -pdf-frame-content: footer_mid;
        bottom: 1cm;
		left: 8cm;
		right: 5cm;
        height: 1.5cm;
        <xsl:value-of select="$pdf-frame-border"/>
    }
    @frame footer_right {
        -pdf-frame-content: footer_right;
        bottom: 1cm;
		left: 17cm;
		right: 2cm;
        height: 1.5cm;
        <xsl:value-of select="$pdf-frame-border"/>
    }
	
    @frame footer_hr {
        -pdf-frame-content: footer_hr;
        bottom: 2.7cm;
		left: 2cm;
		right: 2cm;
        height: 0.25cm;
        <xsl:value-of select="$pdf-frame-border"/>
    }
}
</xsl:template>

<xsl:template match="dsc" mode="pdf-head">

    <xsl:variable name="pdf-frame-border" select="if ($pdfgen='debug') then '-pdf-frame-border: 1;' else ''">
    </xsl:variable>

    <xsl:variable name="dscID" ><xsl:value-of select="translate(@id, '.', '_')"/></xsl:variable>

@page sec_<xsl:value-of select="$dscID"/>{
	size: letter;	
	margin-top: 2cm;
	margin-left: 3cm;
	margin-right: 2cm;
	margin-bottom: 3cm;
    <xsl:value-of select="$pdf-frame-border"/>

	@frame header {
    -pdf-frame-content: header_<xsl:value-of select="$dscID"/>;
		top: .5cm;
		left: 2cm;
		right: 2cm;
		height: .5cm;		
        <xsl:value-of select="$pdf-frame-border"/>
	}

    @frame header_hr {
    -pdf-frame-content: header_hr;
		top: 1.5cm;
		left: 2cm;
		right: 2cm;
		height: .5cm;		
        <xsl:value-of select="$pdf-frame-border"/>
	}
        

    @frame footer_left {
        -pdf-frame-content: footer_left;
        bottom: 1cm;
		left: 2cm;
		right: 14cm;
        height: 1.5cm;
        <xsl:value-of select="$pdf-frame-border"/>
    }
    @frame footer_mid {
        -pdf-frame-content: footer_mid;
        bottom: 1cm;
		left: 8cm;
		right: 5cm;
        height: 1.5cm;
        <xsl:value-of select="$pdf-frame-border"/>
    }
    @frame footer_right {
        -pdf-frame-content: footer_right;
        bottom: 1cm;
		left: 17cm;
		right: 2cm;
        height: 1.5cm;
        <xsl:value-of select="$pdf-frame-border"/>
    }
	
    @frame footer_hr {
        -pdf-frame-content: footer_hr;
        bottom: 2.7cm;
		left: 2cm;
		right: 2cm;
        height: 0.25cm;
        <xsl:value-of select="$pdf-frame-border"/>
    }
}

    <!-- Item needs to be a c01 or c02 to of interest -->
    <xsl:apply-templates select="c01|c02" mode="pdf-head"/>
</xsl:template>

<xsl:template match="c01|c02" mode="pdf-head">

    <xsl:variable name="pdf-frame-border" select="if ($pdfgen='debug') then '-pdf-frame-border: 1;' else ''">
    </xsl:variable>

<xsl:variable 
	name="seriesTrigger" 
	select="if ( (@level='series' or @level='subseries' or @level='recordgrp' or @level='collection') and (local-name()='c01' or local-name()='c02') )
	then 'True' else 'False'"></xsl:variable>

    <xsl:if test="$seriesTrigger = 'True'">
    @page sec_<xsl:value-of select="translate(@id, '.', '_')"/> {
	
	size: letter;	
	margin-top: 1.7cm;
	margin-left: 3cm;
	margin-right: 2cm;
	margin-bottom: 3cm;
    <xsl:value-of select="$pdf-frame-border"/>

					
	@frame header {
    <xsl:choose>
    <xsl:when test="local-name() = 'c01'">
    -pdf-frame-content: header_<xsl:value-of select="translate(@id, '.', '_')"/>;
</xsl:when>
    <xsl:otherwise>
    -pdf-frame-content: header_<xsl:value-of select="translate(../@id, '.', '_')"/>;
</xsl:otherwise>
</xsl:choose>
		top: .5cm;
		left: 2cm;
		right: 2cm;
		height: .5cm;		
        <xsl:value-of select="$pdf-frame-border"/>
	}

    @frame header_hr {
    -pdf-frame-content: header_hr;
		top: 1.5cm;
		left: 2cm;
		right: 2cm;
		height: .25cm;		
        <xsl:value-of select="$pdf-frame-border"/>
	}
        

	@frame subheader {
        -pdf-frame-content: subheader_<xsl:value-of select="translate(@id, '.', '_')"/>;
		top: 1cm;
		left: 2.5cm;
		right: 2cm;
		height: .5cm;		
        <xsl:value-of select="$pdf-frame-border"/>
	}

    @frame footer_left {
        -pdf-frame-content: footer_left;
        bottom: 1cm;
		left: 2cm;
		right: 14cm;
        height: 1.5cm;
        <xsl:value-of select="$pdf-frame-border"/>
    }
    @frame footer_mid {
        -pdf-frame-content: footer_mid;
        bottom: 1cm;
		left: 8cm;
		right: 5cm;
        height: 1.5cm;
        <xsl:value-of select="$pdf-frame-border"/>
    }
    @frame footer_right {
        -pdf-frame-content: footer_right;
        bottom: 1cm;
		left: 17cm;
		right: 2cm;
        height: 1.5cm;
        <xsl:value-of select="$pdf-frame-border"/>
    }
	
    @frame footer_hr {
        -pdf-frame-content: footer_hr;
        bottom: 2.7cm;
		left: 2cm;
		right: 2cm;
        height: 0.25cm;
        <xsl:value-of select="$pdf-frame-border"/>
    }
	
}
<!--<xsl:apply-templates select="c01|c02" mode="pdf-head"/> -->

</xsl:if> <!-- $seriesTrigger = 'True' -->

<xsl:apply-templates select="c01|c02" mode="pdf-head"/>

</xsl:template>

<xsl:template match="c01|c02|c03|c04|c05|c06|c07|c08|c09|c10|c11|c12"
    name="pdfClevel" mode="pdf"> 

    <xsl:param name="tableStart" select="false()"/>
    <!--
    <xsl:message>
        tableStart = <xsl:copy-of select="$tableStart"/>
        element = <xsl:copy-of select="local-name()"/>
    </xsl:message>
    -->

<xsl:variable 
	name="seriesTrigger" 
	select="if ( (@level='series' or @level='subseries' or @level='recordgrp' or @level='collection') and (local-name()='c01' or local-name()='c02') )
	then ' hr' else ''"></xsl:variable>

    <xsl:variable name="pdf-header-background" select="if ($pdfgen='debug') then 'background-color: red;' else ''">
    </xsl:variable>
    <xsl:variable name="pdf-subheader-background" select="if ($pdfgen='debug')
        then 'background-color: orange;' else ''">
    </xsl:variable>

    <xsl:variable name="seriesID" ><xsl:value-of select="translate(@id, '.', '_')"/></xsl:variable>

<xsl:if test="((local-name()='c01') and ($seriesTrigger != ''))">
    <pdf:nextpage name="sec_{$seriesID}" />
    <div class="pdf-header" id="header_{$seriesID}" style="display:inline;
        white-space: nowrap;{$pdf-header-background}" >
        <xsl:apply-templates select=" did/unitid | did/unitdate | did/unittitle " mode="ead-dsc"/>
		<xsl:apply-templates select="did/dao | did/daogrp" mode="ead-dsc"/>
    </div>
    <div class="pdf-header" id="subheader_{$seriesID}" ></div>
</xsl:if>
<xsl:if test="((local-name()='c02') and ($seriesTrigger != ''))">
    <pdf:nexttemplate name="sec_{$seriesID}" />
    <div class="pdf-header" id="subheader_{$seriesID}" style="display:inline; white-space: nowrap;{$pdf-subheader-background}" >
        <xsl:apply-templates select=" did/unitid | did/unitdate | did/unittitle " mode="ead-dsc"/>
			<xsl:apply-templates select="did/dao | did/daogrp" mode="ead-dsc"/>
        </div>
</xsl:if>

    <xsl:variable name="pdf-th-background" select="if ($pdfgen='debug') then 'background-color: red;' else ''">
    </xsl:variable>

<xsl:choose>
    <xsl:when test="$seriesTrigger != '' or $tableStart">

        <table cellspacing="0pt" cellpadding="0pt"> <!--border="1"-->
    <tr valign="top">
        <th style="width: 15%;{$pdf-th-background}"></th>
        <th style="{$pdf-th-background}"></th>
    </tr>

    <xsl:call-template name="pdfrows" />

</table>
</xsl:when><!-- <xsl:when test="$seriesTrigger != ''"> -->
<xsl:otherwise><!-- not a series, just rows no table -->
    <xsl:call-template name="pdfrows" />
</xsl:otherwise><!-- not a series, just rows no table -->
</xsl:choose>

</xsl:template>


<xsl:template name="pdfrows">
<xsl:variable 
	name="seriesTrigger" 
	select="if ( (@level='series' or @level='subseries' or @level='recordgrp' or @level='collection') and (local-name()='c01' or local-name()='c02') )
	then ' hr' else ''"></xsl:variable>

<xsl:variable 
	name="itemIndent" 
	select="concat((number(substring(local-name(),3,1))-2)*2,'em')"></xsl:variable>

            <xsl:variable name="hasNotes" select="boolean(
did/abstract| did/head| did/langmaterial| did/materialspec| did/physdesc| did/note| did/origination| did/physloc| 
did/repository |
accessrestrict | accruals | acqinfo | altformavail | appraisal | arrangement | bibliography | bioghist | 
controlaccess | custodhist | fileplan | head | index | note | odd | dsc | originalsloc | otherfindaid | 
phystech | prefercite | processinfo | relatedmaterial | scopecontent | separatedmaterial | thead | userestrict)"
/>

<div class="cx{$seriesTrigger}">
    <xsl:if test="@id">
      <xsl:attribute name="id" select="@id"/>
    </xsl:if>
    <tr valign="top">
      <td valign="top">

        <div class="c">
    	<xsl:choose>
    	  <xsl:when test="did/container">
    		<xsl:apply-templates select="did/container" mode="container"/>
    	  </xsl:when>
    	  <xsl:otherwise>
    		<xsl:text>&#160;</xsl:text>
    	  </xsl:otherwise>
    	</xsl:choose>
        </div>

       </td>

  <td valign="top" style="margin-left: {$itemIndent};">

         <div class="{name()}">
		<p>
            <xsl:if test="$seriesTrigger = ' hr'">
                <xsl:variable 
                	name="pdfOutlineStyle" 
                    select="concat('-pdf-outline: true;', ' ',
                        '-pdf-outline-open: false;', ' ',
                        '-pdf-outline-level: ',
                        number((substring-after(name(),'c'))),'; '
                    )"
                 />

                <xsl:attribute name='style' select="$pdfOutlineStyle"/>
            </xsl:if>
			<!-- xsl:apply-templates select="did" mode="ead"/ -->
            <xsl:apply-templates select="did/unitid | did/unitdate | did/unittitle " mode="ead-dsc"/>
			<xsl:apply-templates select="did/dao | did/daogrp" mode="ead-dsc"/>
		</p>
        <!-- this stuff needs to go into next row.... -->
	<xsl:if test="$hasNotes">
	<div class="c0x-notes"> 
		<xsl:apply-templates select="did/abstract| did/head| did/langmaterial| did/materialspec| 
			did/physdesc|
			did/note| did/origination| did/physloc| did/repository" mode="ead"/>
		<xsl:apply-templates select="accessrestrict | accruals | acqinfo | altformavail | 
			appraisal | arrangement | bibliography | bioghist | 
			controlaccess | custodhist | fileplan | head | 
			index | note | odd | dsc | originalsloc | otherfindaid | 
			phystech | prefercite | processinfo | relatedmaterial | 
			scopecontent | separatedmaterial | thead | userestrict" mode="ead"/>
	</div>
	</xsl:if>
  </div>

  </td>
  </tr>
  <xsl:if test="$hasNotes or $seriesTrigger = ' hr'">
    <tr><td>&#160;</td><td>&#160;</td></tr>
  </xsl:if>
</div>

<xsl:if test="(($seriesTrigger = ' hr') and (local-name() != 'c01'))">
        <hr/>
</xsl:if>

<xsl:apply-templates select="c01|c02|c03|c04|c05|c06|c07|c08|c09|c10|c11|c12"
    mode="pdf"/>

</xsl:template>


<xsl:template match="dao" mode="ead-dsc">
<xsl:variable name="hackedLink" select="
        replace(replace(dao[1]/@href,'http://ark.cdlib.org/ark:/', concat('/' , 'ark:/') ) ,'/$','')" />
        <xsl:variable name="link">
		   <xsl:choose>
			<xsl:when test="@poi">
                <xsl:text>http://content.cdlib.org/</xsl:text>
				<xsl:value-of select="@poi"/>
                <!--
				<xsl:text>/?brand=oac4</xsl:text>
                -->
			</xsl:when>
			<xsl:when test="@href
                        		and ( starts-with(@role,'http://oac.cdlib.org/arcrole/link') )
                        		and not ( starts-with(@href,'http://ark.cdlib.org/ark:') )
                        		and not ( starts-with(@href,'/ark:/13030/') )
                        		or ( ends-with(@content-role,'link/text') )
			">
                <xsl:text>http://content.cdlib.org/</xsl:text>
				<xsl:value-of select="@href"/>
			</xsl:when>
			<xsl:when test="starts-with(@href,'http://ark.cdlib.org/ark:/')
                     			or starts-with(@href,'/ark:/13030/')
			">
                <xsl:text>http://content.cdlib.org/</xsl:text>
				<xsl:value-of select="$hackedLink"/>
                <!--
				<xsl:text>/?brand=oac4</xsl:text>
                -->
			</xsl:when>
			<xsl:otherwise/>
		   </xsl:choose>
       </xsl:variable>

       <xsl:call-template name="online-items-graphic-element">
		<xsl:with-param name="href" select="$link"/>
        <xsl:with-param name="img_src"
            select="'./images/eye_icon.gif'"/>
        <xsl:with-param name="text">
            <xsl:value-of select="$link"/>
        </xsl:with-param>
       </xsl:call-template>
</xsl:template> 

<xsl:template match="daogrp" mode="ead-dsc" >
		   <xsl:variable name="link">
               <xsl:text>http://content.cdlib.org/</xsl:text>
			   <xsl:value-of select="@poi"/>
            <!--
			<xsl:text>/?brand=oac4</xsl:text>
            -->
		   </xsl:variable>
       <xsl:call-template name="online-items-graphic-element">
		<xsl:with-param name="href" select="$link"/>
        <xsl:with-param name="img_src"
            select="'./images/eye_icon.gif'"/>
        <xsl:with-param name="text">
            <xsl:value-of select="$link"/>
        </xsl:with-param>
       </xsl:call-template>
</xsl:template> 

<!--
<xsl:template match="unitid" mode="ead-dsc">
<xsl:value-of select="replace(.,'\s','&#160;')"/>
<xsl:text> </xsl:text>
</xsl:template>
-->

</xsl:stylesheet>
