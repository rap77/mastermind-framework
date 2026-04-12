import React from 'react'

export const Virtuoso = React.forwardRef<any, any>((props, ref) => {
  const { data, itemContent, className, style, ...rest } = props

  return (
    <div className={className} style={style} {...rest} ref={ref}>
      {data.map((item: any, index: number) => (
        <div key={item?.id || index} data-testid={`virtuoso-item-${index}`}>
          {itemContent(index, item)}
        </div>
      ))}
    </div>
  )
})
