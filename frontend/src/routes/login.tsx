import { createFileRoute, redirect, useNavigate } from '@tanstack/react-router'
import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form";
import type { SubmitHandler } from "react-hook-form";
import type { AuthFormValues } from '@/utils/form-schema';
import { authSchema } from '@/utils/form-schema';
import { tryCatch } from '@/utils/try-catch';
import { setStoredUser, useAuth } from '@/integrations/auth/root-provider';


export const Route = createFileRoute('/login')({
  beforeLoad: ({ context }) => {
    if (context.auth?.user != null) {
      throw redirect({
        to: '/',
      })
    }
  },
  component: RouteComponent,
})

function RouteComponent() {
  const navigate = useNavigate()
  const auth = useAuth()

  const {
    register,
    handleSubmit,
    setError,
    formState: { errors },
  } = useForm<AuthFormValues>({
    resolver: zodResolver(authSchema)
  })

  const onSubmit: SubmitHandler<AuthFormValues> = async (form_data) => {

    const [res, error] = await tryCatch(fetch(import.meta.env.VITE_API_HOST + "/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(form_data),
      credentials: "include"
    }));

    if (error) {
      setError("root", { message: error.message });
      return;
    }

    const data = await res.json();

    if (!res.ok) {
      setError("root", { message: data["detail"] })
      return;
    }

    setStoredUser(data.username, auth)

    navigate({
      to: '/',
    })
  }

  return (
    <div className="flex justify-center mt-20">
      <form
        onSubmit={handleSubmit(onSubmit)}
        className="flex flex-col bg-slate-800 p-8 rounded-2xl shadow-lg w-full max-w-sm gap-5"
      >
        <h1 className="text-2xl font-semibold text-center mb-2">
          Login
        </h1>

        <div className="flex flex-col gap-1 text-sm">
          <label className="text-gray-300">Username</label>
          <input
            {...register("username")}
            className="p-2 rounded-md bg-slate-700 border border-slate-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          {errors.username && (
            <p className="text-red-400">{errors.username.message}</p>
          )}
        </div>

        <div className="flex flex-col gap-1 text-sm">
          <label className="text-gray-300">Password</label>
          <input
            type="password"
            {...register("password")}
            className="p-2 rounded-md bg-slate-700 border border-slate-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          {errors.password && (
            <p className="text-red-400">{errors.password.message}</p>
          )}
        </div>

        {errors.root && (
          <p className="text-red-400">{errors.root.message}</p>
        )}

        <input
          type="submit"
          value="Login"
          className="mt-4 bg-blue-600 hover:bg-blue-700 transition-colors font-semibold py-2 rounded-md cursor-pointer"
        />
      </form>
    </div>
  )
}
