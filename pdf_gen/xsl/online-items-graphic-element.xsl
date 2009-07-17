<xsl:stylesheet version="2.0"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
xmlns:mets="http://www.loc.gov/METS/"
>

<xsl:template name="online-items-graphic-element">
	<xsl:param name="href"/>
	<xsl:param name="class" select="'collection-items'"/>
	<xsl:param name="text" select="'Online items available'"/>
	<xsl:param name="onclick"/>
    <xsl:param name="img_src" select="'./images/eye_icon.gif'"/>
	<xsl:param name="element" select="'span'"/>
	<xsl:element name="{$element}">
		<xsl:attribute name="class" select="$class"/>
		<img width="15" height="9" title="Online items available" alt="Online items available" 
            src="{$img_src}" class="eye-icon"/>
		<span class="online-items">
			<xsl:choose>
				<xsl:when test="$href != ''">
			<a href="{$href}">
				<xsl:if test="$onclick != ''">
					<xsl:attribute name="onclick">
						<xsl:value-of select="$onclick"/>
					</xsl:attribute>
				</xsl:if>
				<xsl:value-of select="$text"/>
			</a>
				</xsl:when>
				<xsl:otherwise>
			<xsl:value-of select="$text"/>
				</xsl:otherwise>
			</xsl:choose>
		</span>
	</xsl:element>
</xsl:template>


<!-- BSD license copyright 2009 -->
</xsl:stylesheet>
