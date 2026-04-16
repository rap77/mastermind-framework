import * as React from "react"
import { Input as InputPrimitive } from "@base-ui/react/input"
import { cva, type VariantProps } from "class-variance-authority"

import { cn } from "@/lib/utils"

const inputVariants = cva(
  "h-8 w-full min-w-0 rounded-lg border bg-transparent px-2.5 py-1 text-base transition-colors outline-none file:inline-flex file:h-6 file:border-0 file:bg-transparent file:text-sm file:font-medium file:text-foreground placeholder:text-muted-foreground focus-visible:ring-3 disabled:pointer-events-none disabled:cursor-not-allowed disabled:opacity-50 md:text-sm",
  {
    variants: {
      variant: {
        default:
          "border-input focus-visible:border-ring focus-visible:ring-ring/50 bg-transparent dark:bg-input/30 disabled:bg-input/50 dark:disabled:bg-input/80",
        error:
          "border-destructive focus-visible:border-destructive focus-visible:ring-destructive/20 aria-invalid:ring-3 aria-invalid:ring-destructive/20 dark:border-destructive/50 dark:focus-visible:ring-destructive/40 dark:aria-invalid:ring-destructive/40",
      },
      size: {
        sm: "h-7 px-2 text-sm",
        md: "h-8 px-2.5 text-base",
        lg: "h-10 px-3 text-lg",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "md",
    },
  }
)

export interface InputProps
  extends React.ComponentProps<"input">,
    VariantProps<typeof inputVariants> {
  label?: string
  error?: string
  leftIcon?: React.ReactNode
  rightIcon?: React.ReactNode
  containerClassName?: string
}

function Input({
  className,
  containerClassName,
  variant,
  size,
  label,
  error,
  leftIcon,
  rightIcon,
  type,
  id,
  ...props
}: InputProps) {
  const inputId = id || React.useId()
  const hasError = Boolean(error)

  return (
    <div className={cn("flex flex-col gap-1.5", containerClassName)}>
      {label && (
        <label
          htmlFor={inputId}
          className="text-sm font-medium text-foreground leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
        >
          {label}
        </label>
      )}
      <div className="relative">
        {leftIcon && (
          <div className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground pointer-events-none">
            {leftIcon}
          </div>
        )}
        <InputPrimitive
          type={type}
          data-slot="input"
          id={inputId}
          className={cn(
            inputVariants({ variant: hasError ? "error" : variant, size }),
            leftIcon && "pl-10",
            rightIcon && "pr-10",
            className
          )}
          aria-invalid={hasError}
          {...props}
        />
        {rightIcon && (
          <div className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground pointer-events-none">
            {rightIcon}
          </div>
        )}
      </div>
      {error && (
        <p className="text-sm text-destructive font-medium" role="alert">
          {error}
        </p>
      )}
    </div>
  )
}

export { Input, inputVariants }
