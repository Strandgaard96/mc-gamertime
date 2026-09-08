import { Loader2 } from "lucide-react";
import { type ButtonHTMLAttributes, cloneElement, forwardRef, isValidElement } from "react";
import { cn, pressable } from "../../lib/utils";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "default" | "outline" | "ghost" | "destructive";
  size?: "default" | "sm" | "lg" | "icon";
  isLoading?: boolean;
  asChild?: boolean;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      className,
      variant = "default",
      size = "default",
      isLoading,
      asChild,
      children,
      disabled,
      ...props
    },
    ref,
  ) => {
    const classes = cn(
      "inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50",
      {
        default: "bg-primary text-primary-foreground hover:bg-primary/90",
        outline: "border border-input bg-background hover:bg-accent hover:text-accent-foreground",
        ghost: "hover:bg-accent hover:text-accent-foreground",
        destructive: "bg-destructive text-destructive-foreground hover:bg-destructive/90",
      }[variant],
      {
        default: "h-10 px-4 py-2",
        sm: "h-9 rounded-md px-3",
        lg: "h-11 rounded-md px-8",
        icon: "h-10 w-10",
      }[size],
      // Must come after the base transition-colors so it wins the tailwind-merge conflict
      pressable,
      className,
    );

    if (asChild && isValidElement(children)) {
      const child = children as React.ReactElement<any>;
      return cloneElement(child, {
        className: cn(classes, child.props.className),
        ref,
        ...props,
      });
    }

    return (
      <button ref={ref} disabled={disabled || isLoading} className={classes} {...props}>
        {isLoading && <Loader2 size={14} className="mr-2 animate-spin shrink-0" />}
        {children}
      </button>
    );
  },
);
Button.displayName = "Button";
